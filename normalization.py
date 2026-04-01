import os
from pydub import AudioSegment, effects

def normalize_audio():
    source_folder = os.path.join(os.getcwd(), 'segments')
    destination_folder = os.path.join(os.getcwd(), 'normalized_segments')

    files = [f for f in os.listdir(source_folder) if f.lower().endswith('.wav')]

    for filename in files:
        input_path = os.path.join(source_folder, filename)
        output_path = os.path.join(destination_folder, filename)

        try:
            audio = AudioSegment.from_wav(input_path)
            normalized_audio = effects.normalize(audio)
            normalized_audio.export(output_path, format="wav")
            print(f"Normalized: {filename}")
        except Exception as e:
            print(f"Error normalizing {filename}: {e}")

if __name__ == "__main__":
    normalize_audio()