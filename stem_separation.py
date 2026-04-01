import os
import demucs.separate
import shutil
import torch

def separate_stems():
    songs_folder = os.path.join(os.getcwd(), "songs")
    vocals_folder = os.path.join(os.getcwd(), "vocals")
    instrumental_folder = os.path.join(os.getcwd(), "instrumental")
    temp_output = os.path.join(os.getcwd(), "temp_separated")

    files = [f for f in os.listdir(songs_folder) if f.lower().endswith('.mp3')]

    for filename in files:
        song_path = os.path.join(songs_folder, filename)
        song_title = os.path.splitext(filename)[0]

        demucs.separate.main([
            "--two-stems", "vocals",
            "-o", temp_output,
            song_path
        ])

        separated_path = os.path.join(temp_output, "htdemucs", song_title)

        if os.path.exists(separated_path):
            vocals_src = os.path.join(separated_path, "vocals.wav")
            instrumental_src = os.path.join(separated_path, "no_vocals.wav")

            if os.path.exists(vocals_src):
                shutil.move(vocals_src, os.path.join(vocals_folder, f"{song_title}.wav"))

            if os.path.exists(instrumental_src):
                shutil.move(instrumental_src, os.path.join(instrumental_folder, f"{song_title}.wav"))

    if os.path.exists(temp_output):
        shutil.rmtree(temp_output)

if __name__ == "__main__":
    separate_stems()