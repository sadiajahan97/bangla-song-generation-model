import os
import psycopg2

def insert_segment_titles():
    db_params = {
        "host": "localhost",
        "database": "ai_music_mind",
        "user": "sadia-iffat-jahan"
    }

    segments_folder = os.path.join(os.getcwd(), "segments")

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        files = [f for f in os.listdir(segments_folder) if f.lower().endswith('.wav')]

        inserted_count = 0
        for filename in files:
            segment_title = os.path.splitext(filename)[0]

            if "_Segment_" in segment_title:
                song_title = segment_title.split("_Segment_")[0]
            else:
                print(f"Skipping {filename}: does not contain '_Segment_'")
                continue

            cur.execute("SELECT id FROM songs WHERE title = %s", (song_title,))
            result = cur.fetchone()

            if result:
                song_id = result[0]

                cur.execute("SELECT 1 FROM segments WHERE title = %s", (segment_title,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO segments (title, song_id) VALUES (%s, %s)", (segment_title, song_id))
                    inserted_count += 1
            else:
                print(f"Warning: Song title '{song_title}' not found in 'songs' table for segment '{segment_title}'")

        conn.commit()
        print(f"Successfully inserted {inserted_count} segment titles into the 'segments' table.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    insert_segment_titles()