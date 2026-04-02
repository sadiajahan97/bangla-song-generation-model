import os
import json
import psycopg2

def create_master_dataset():
    db_params = {
        "host": "localhost",
        "database": "ai_music_mind",
        "user": "sadia-iffat-jahan"
    }

    output_file = os.path.join(os.getcwd(), "dataset.jsonl")
    segments_folder = "normalized_segments"

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        cur.execute("SELECT title, lyrics, genre, tempo_bpm, key FROM segments")
        rows = cur.fetchall()

        print(f"Creating master dataset for {len(rows)} segments...")

        with open(output_file, "w", encoding="utf-8") as f:
            for title, lyrics, genre, tempo, key in rows:
                audio_path = os.path.join(segments_folder, f"{title}.wav")

                data = {
                    "title": title,
                    "audio_path": audio_path,
                    "genre": genre,
                    "lyrics": lyrics,
                    "tempo": tempo,
                    "key": key
                }

                f.write(json.dumps(data, ensure_ascii=False) + "\n")

        print(f"Successfully generated dataset.jsonl with {len(rows)} entries.")

    except Exception as e:
        print(f"Error generating dataset: {e}")
    finally:
        if 'conn' in locals() and conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    create_master_dataset()