import os
import subprocess

def sample_songs():
    source_folder = os.path.join(os.getcwd(), 'songs')
    destination_folder = os.path.join(os.getcwd(), 'sampled_songs')

    files = [f for f in os.listdir(source_folder) if f.lower().endswith('.mp3')]

    print(f"Sampling {len(files)} songs to 22.05 kHz...")

    for filename in files:
        input_path = os.path.join(source_folder, filename)
        output_filename = os.path.splitext(filename)[0] + '.wav'
        output_path = os.path.join(destination_folder, output_filename)

        print(f"Processing: {filename} -> {output_filename}")

        command = [
            'ffmpeg',
            '-i', input_path,
            '-ar', '22050',
            '-y',
            output_path
        ]

        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {filename}: {e.stderr.decode('utf-8')}")

    print("Sampling completed.")

if __name__ == "__main__":
    sample_songs()