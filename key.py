import os
import psycopg2
import essentia.standard as es

def update_segment_keys():
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

        print(f"Extracting key for {len(files)} normalized segments using Essentia...")

        updated_count = 0
        for filename in files:
            title = os.path.splitext(filename)[0]
            full_path = os.path.join(normalized_segments_folder, filename)

            try:
                audio = es.MonoLoader(filename=full_path)()

                key_extractor = es.KeyExtractor()
                key, scale, strength = key_extractor(audio)

                key_scale = f"{key} {scale}"
                print(f"Processing: {title} | Key: {key_scale} (Confidence: {strength:.2f})")

                cur.execute(
                    "UPDATE segments SET key = %s WHERE title = %s",
                    (key_scale, title)
                )

                if cur.rowcount > 0:
                    updated_count += 1
                else:
                    print(f"Warning: Segment '{title}' not found in database.")

            except Exception as e:
                print(f"Error extracting key for {filename}: {e}")

        conn.commit()
        print(f"Successfully updated 'key' for {updated_count} segments.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if 'conn' in locals() and conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    update_segment_keys()