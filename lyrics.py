import os
import requests
import psycopg2
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def transcribe_lyrics():
    db_params = {
        "host": "localhost",
        "database": "ai_music_mind",
        "user": "sadia-iffat-jahan"
    }

    segments_folder = os.path.join(os.getcwd(), "normalized_segments")
    api_url = "https://192.168.101.231:8569/transcribe"

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        cur.execute("SELECT title FROM segments WHERE lyrics IS NULL OR lyrics = ''")
        to_process = {row[0] for row in cur.fetchall()}

        all_files = [f for f in os.listdir(segments_folder) if f.lower().endswith('.wav')]
        files = [f for f in all_files if os.path.splitext(f)[0] in to_process]

        print(f"Processing {len(files)} segments via remote API...")

        for i, filename in enumerate(files, 1):
            title = os.path.splitext(filename)[0]
            full_path = os.path.join(segments_folder, filename)

            try:
                with open(full_path, "rb") as audio_file:
                    files_payload = {"audio": (filename, audio_file, "audio/wav")}
                    response = requests.post(api_url, files=files_payload, verify=False, timeout=60)

                if response.status_code == 200:
                    transcription = response.json()
                    lyrics = transcription.strip() if transcription and transcription.strip() else "[Instrumental]"
                elif response.status_code == 422:
                    lyrics = "[Validation Error]"
                    print(f"Validation Error (422) for {title}: {response.json()}")
                else:
                    lyrics = f"[Error {response.status_code}]"
                    print(f"API Error ({response.status_code}) for {title}")

                cur.execute(
                    "UPDATE segments SET lyrics = %s WHERE title = %s",
                    (lyrics, title)
                )

                if i % 10 == 0:
                    conn.commit()

                print(f"[{i}/{len(files)}] {title} -> {lyrics[:50]}...")

            except Exception as e:
                print(f"Request Error on {filename}: {e}")

        conn.commit()
        print("API Transcription process completed.")

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    transcribe_lyrics()