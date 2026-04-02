# Bangla Songs Audio Processing Pipeline

This project contains a suite of Python scripts designed to process audio files, extract musical features, and manage metadata in a PostgreSQL database (`ai_music_mind`).

## Project Structure

- `songs/`: Source directory for original MP3 files.
- `sampled_songs/`: Songs resampled to 22.05 kHz WAV format.
- `segments/`: 10-second segments with 5-second overlap.
- `normalized_segments/`: Final normalized audio segments.
- `vocals/`: Extracted vocal stems for transcription.

## Prerequisites

Ensure you have the following dependencies installed (as listed in `requirements.txt`):

- `librosa`: For audio sampling and BPM detection.
- `essentia-tensorflow`: For musical key detection and genre classification.
- `pydub`: For audio normalization.
- `pyAudioAnalysis`: For audio segmentation.
- `psycopg2-binary`: For PostgreSQL database connectivity.
- `ffmpeg`: Required for audio transcoding.
- `demucs`: For source (stem) separation.
- `eyed3`: For handling MP3 metadata.
- `torchcodec`: For optimized audio decoding and processing.
- `requests`: For interacting with remote transcription APIs.

## Execution Order

The scripts must be executed in the following sequence to ensure proper data flow and dependency management:

1.  **`renaming.py`**: Standardizes original filenames in the `songs/` folder.
2.  **`title.py`**: Initializes the `songs` table by extracting filenames from the `songs/` folder.
3.  **`sampling.py`**: Resamples songs to 22.05 kHz WAV format and stores them in `sampled_songs/`.
4.  **`segmentation.py`**: Slices sampled songs into overlapping 10-second segments stored in `segments/`.
5.  **`segment_title.py`**: Initializes the `segments` table and links segments to their original songs.
6.  **`normalization.py`**: Normalizes the audio levels of the segments and saves them to `normalized_segments/`.
7.  **`tempo_bpm.py`**: Estimates the BPM of normalized segments and updates the `segments` table.
8.  **`key.py`**: Detects the musical key of normalized segments and updates the `segments` table.
9.  **`genre.py`**: Detects the musical genre of segments using pre-trained TensorFlow models and updates the `segments` table.
10. **`stem_separation.py`**: Extracts vocal stems from normalized segments (using batch processing) and saves them in the `vocals/` folder.
11. **`lyrics.py`**: Transcribes lyrics for the extracted vocal stems via a remote ASR API and updates the `segments` table.
12. **`master_dataset.py`**: Consolidates all segment metadata (lyrics, genre, tempo, key) and normalized audio paths into a unified `dataset.jsonl` file.

## Database Configuration

The pipeline interacts with a local PostgreSQL database named `ai_music_mind`. Ensure the database is running and accessible with the parameters defined in the scripts.

---
*Note: Other utility scripts in the directory should be ignored as they are not part of the primary processing pipeline.*
