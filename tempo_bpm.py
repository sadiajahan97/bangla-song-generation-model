import os
import librosa
import psycopg2

def update_tempo_bpm():
    db_params = {
        "host": "localhost",
        "database": "ai_music_mind",
        "user": "sadia-iffat-jahan"
    }

    normalized_segments_folder = os.path.join(os.getcwd(), "normalized_segments")

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        files = [f for f in os.listdir(normalized_segments_folder) if f.lower().endswith('.wav')]

        print(f"Calculating BPM for {len(files)} normalized segments...")

        updated_count = 0
        for filename in files:
            title = os.path.splitext(filename)[0]
            full_path = os.path.join(normalized_segments_folder, filename)

            try:
                y, sr = librosa.load(full_path, sr=None)

                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

                if hasattr(tempo, "__len__"):
                    bpm = float(tempo[0])
                else:
                    bpm = float(tempo)

                print(f"Processing: {title} | Estimated BPM: {bpm:.2f}")

                cur.execute(
                    "UPDATE segments SET tempo_bpm = %s WHERE title = %s",
                    (bpm, title)
                )

                if cur.rowcount > 0:
                    updated_count += 1
                else:
                    print(f"Warning: Segment '{title}' not found in database.")

            except Exception as e:
                print(f"Error calculating BPM for {filename}: {e}")

        conn.commit()
        print(f"Successfully updated 'tempo_bpm' for {updated_count} segments.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if 'conn' in locals() and conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    update_tempo_bpm()