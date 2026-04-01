import os
import psycopg2

def extract_titles_and_insert():
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

        inserted_count = 0
        for filename in files:
            if filename.lower().endswith('.mp3'):
                title = os.path.splitext(filename)[0]

                cur.execute("SELECT id FROM songs WHERE title = %s", (title,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO songs (title) VALUES (%s)", (title,))
                    inserted_count += 1
        
        conn.commit()
        print(f"Successfully inserted {inserted_count} song titles into the 'songs' table.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    extract_titles_and_insert()