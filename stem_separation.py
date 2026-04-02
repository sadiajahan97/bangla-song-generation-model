import os
import demucs.separate
import shutil
import torch

def separate_stems():
    segments_folder = os.path.join(os.getcwd(), "normalized_segments")
    vocals_folder = os.path.join(os.getcwd(), "vocals")
    temp_output = os.path.join(os.getcwd(), "temp_separated")

    existing_vocals = {os.path.splitext(f)[0] for f in os.listdir(vocals_folder) if f.lower().endswith('.wav')}
    all_files = [f for f in os.listdir(segments_folder) if f.lower().endswith('.wav')]
    target_files = [f for f in all_files if os.path.splitext(f)[0] not in existing_vocals]

    if not target_files:
        print("All segments have already been processed.")
        return

    print(f"Total segments: {len(all_files)}")
    print(f"Segments to process: {len(target_files)}")

    batch_size = 10
    total_batches = (len(target_files) + batch_size - 1) // batch_size

    try:
        for i in range(0, len(target_files), batch_size):
            batch = target_files[i:i + batch_size]
            batch_paths = [os.path.join(segments_folder, f) for f in batch]
            current_batch_num = i // batch_size + 1

            print(f"[{current_batch_num}/{total_batches}] Processing batch of {len(batch)} files...")

            try:
                demucs.separate.main([
                    "--two-stems", "vocals",
                    "-o", temp_output,
                    *batch_paths
                ])

                for filename in batch:
                    segment_title = os.path.splitext(filename)[0]
                    separated_path = os.path.join(temp_output, "htdemucs", segment_title)

                    if os.path.exists(separated_path):
                        vocals_src = os.path.join(separated_path, "vocals.wav")
                        if os.path.exists(vocals_src):
                            shutil.move(vocals_src, os.path.join(vocals_folder, f"{segment_title}.wav"))

                if os.path.exists(temp_output):
                    shutil.rmtree(temp_output)

            except Exception as e:
                print(f"Error processing batch {current_batch_num}: {e}")
    finally:
        if os.path.exists(temp_output):
            shutil.rmtree(temp_output)

if __name__ == "__main__":
    separate_stems()