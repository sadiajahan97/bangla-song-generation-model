import os
import numpy as np
from pyAudioAnalysis import audioBasicIO
import wave

def segment_sampled_songs():
    source_folder = os.path.join(os.getcwd(), 'sampled_songs')
    destination_folder = os.path.join(os.getcwd(), 'segments')

    files = [f for f in os.listdir(source_folder) if f.lower().endswith('.wav')]

    print(f"Segmenting {len(files)} songs into 10s segments with 5s overlap using pyAudioAnalysis patterns...")

    for filename in files:
        input_path = os.path.join(source_folder, filename)
        title = os.path.splitext(filename)[0]

        try:
            fs, x = audioBasicIO.read_audio_file(input_path)
            x = np.array(x)
            duration = len(x) / float(fs)

            segment_duration = 10
            overlap_duration = 5
            step_duration = segment_duration - overlap_duration

            print(f"Processing: {title} (Total duration: {duration:.2f}s, Sampling Rate: {fs}Hz)")

            segment_index = 1
            step_samples = int(step_duration * fs)
            segment_samples = int(segment_duration * fs)

            while ((segment_index - 1) * step_samples) + segment_samples <= len(x):
                start_sample = (segment_index - 1) * step_samples
                end_sample = start_sample + segment_samples
                segment = x[start_sample:end_sample]

                output_filename = f"{title}_Segment_{segment_index}.wav"
                output_path = os.path.join(destination_folder, output_filename)

                num_channels = 1 if len(segment.shape) == 1 else segment.shape[1]

                with wave.open(output_path, 'wb') as f:
                    f.setnchannels(num_channels)
                    f.setsampwidth(2)
                    f.setframerate(int(fs))

                    if segment.dtype != np.int16:
                        segment_to_save = (np.clip(segment, -1, 1) * 32767).astype(np.int16)
                    else:
                        segment_to_save = segment

                    f.writeframes(segment_to_save.tobytes())

                segment_index += 1

            print(f"Generated {segment_index} segments for {title}")

        except Exception as e:
            print(f"Error segmenting {filename}: {e}")

    print("Segmentation completed.")

if __name__ == "__main__":
    segment_sampled_songs()