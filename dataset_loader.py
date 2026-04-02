import json
import os
from pathlib import Path

import torch
import torchaudio
import torchaudio.transforms as T
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence

class BanglaSongDataset(Dataset):
    def __init__(
        self,
        jsonl_path: str = "dataset.jsonl",
        sample_rate: int = 22050,
        n_fft: int = 2048,
        hop_length: int = 512,
        n_mels: int = 128,
        f_min: float = 20.0,
        f_max: float = 8000.0,
        top_db: float = 80.0,
        max_frames: int = 431,
    ):
        self.jsonl_path = Path(jsonl_path)
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.f_min = f_min
        self.f_max = f_max
        self.top_db = top_db
        self.max_frames = max_frames

        self.mel_transform = T.MelSpectrogram(
            sample_rate=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=self.n_mels,
            f_min=self.f_min,
            f_max=self.f_max,
        )
        self.amplitude_to_db = T.AmplitudeToDB(top_db=self.top_db)

        self.samples = self._load_samples()
        print(f"Loaded {len(self.samples)} samples from {self.jsonl_path}")

    def _load_samples(self) -> list[dict]:
        samples = []
        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                samples.append(json.loads(line))
        return samples

    def _load_mel(self, audio_path: str) -> torch.Tensor:
        waveform, sr = torchaudio.load(audio_path)

        if sr != self.sample_rate:
            waveform = torchaudio.functional.resample(waveform, orig_freq=sr, new_freq=self.sample_rate)

        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        mel = self.mel_transform(waveform)
        mel = self.amplitude_to_db(mel)
        mel = mel.squeeze(0)
        
        mel = (mel - mel.mean()) / (mel.std() + 1e-6)

        actual_t = mel.shape[-1]
        if actual_t >= self.max_frames:
            mel = mel[:, :self.max_frames]
        else:
            pad = torch.zeros(mel.shape[0], self.max_frames - actual_t)
            mel = torch.cat([mel, pad], dim=-1)

        return mel

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict:
        entry = self.samples[idx]
        mel = self._load_mel(entry["audio_path"])
        return {
            "mel": mel,
            "title": entry.get("title", ""),
            "genre": entry.get("genre", ""),
            "lyrics": entry.get("lyrics", ""),
            "tempo": torch.tensor(entry.get("tempo", 0.0), dtype=torch.float32),
            "key": entry.get("key", ""),
        }

def collate_fn(batch: list[dict]) -> dict:
    mels = [item["mel"].T for item in batch]
    mels = pad_sequence(mels, batch_first=True)
    mels = mels.permute(0, 2, 1)

    return {
        "mel": mels,
        "title": [item["title"] for item in batch],
        "genre": [item["genre"] for item in batch],
        "lyrics": [item["lyrics"] for item in batch],
        "tempo": torch.stack([item["tempo"] for item in batch]),
        "key": [item["key"] for item in batch],
    }

def get_dataloader(
    jsonl_path: str = "dataset.jsonl",
    batch_size: int = 16,
    shuffle: bool = True,
    num_workers: int = 4,
    max_frames: int = 431,
    **kwargs
) -> DataLoader:
    dataset = BanglaSongDataset(
        jsonl_path=jsonl_path,
        max_frames=max_frames,
        **kwargs
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=torch.cuda.is_available(),
    )

    return loader