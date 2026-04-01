import os
import psycopg2
import subprocess
import re

def get_duration(file_path):
    try:
        result = subprocess.run(['afinfo', file_path], capture_output=True, text=True)
        if result.returncode == 0:
            match = re.search(r'estimated duration:\s+([\d\.]+)\s+sec', result.stdout)
            if match:
                return float(match.group(1))
    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
    return None

def update_song_durations():
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
                full_path = os.path.join(songs_folder, filename)

                duration = get_duration(full_path)

                if duration is not None:
                    cur.execute(
                        "UPDATE songs SET duration = %s WHERE title = %s",
                        (duration, title)
                    )

                    if cur.rowcount > 0:
                        updated_count += 1

        conn.commit()
        print(f"Successfully updated 'duration' for {updated_count} songs.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if 'conn' in locals() and conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    update_song_durations()