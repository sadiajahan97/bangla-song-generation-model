import os
import psycopg2

def update_song_file_paths():
    db_params = {
        "host": "localhost",
        "database": "ai_music_mind",
        "user": "sadia-iffat-jahan"
    }

    songs_folder = os.path.join(os.getcwd(), "songs")

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        files = os.listdir(songs_folder)

        updated_count = 0
        for filename in files:
            if filename.lower().endswith('.mp3'):
                title = os.path.splitext(filename)[0]
                full_path = os.path.join("songs", filename)

                cur.execute(
                    "UPDATE songs SET file_path = %s WHERE title = %s",
                    (full_path, title)
                )

                if cur.rowcount > 0:
                    updated_count += 1
        
        conn.commit()
        print(f"Successfully updated 'file_path' for {updated_count} songs.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if 'conn' in locals() and conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    update_song_file_paths()