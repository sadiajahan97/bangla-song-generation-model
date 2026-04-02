import os
import json
import numpy as np
import psycopg2
import essentia.standard as es
import essentia

essentia.log.warningActive = False
essentia.log.infoActive = False

def update_genres():
    db_params = {
        "host": "localhost",
        "database": "ai_music_mind",
        "user": "sadia-iffat-jahan"
    }

    models_dir = os.path.join(os.getcwd(), "models")
    effnet_model = os.path.join(models_dir, "discogs-effnet-bs64-1.pb")
    genre_model = os.path.join(models_dir, "genre_discogs400-discogs-effnet-1.pb")
    genre_json = os.path.join(models_dir, "genre_discogs400.json")
    segments_folder = os.path.join(os.getcwd(), "normalized_segments")

    with open(genre_json, "r") as f:
        labels = json.load(f)["classes"]

    embedding_alg = es.TensorflowPredictEffnetDiscogs(
        graphFilename=effnet_model,
        output="PartitionedCall:1"
    )

    classification_alg = es.TensorflowPredict2D(
        graphFilename=genre_model,
        input="serving_default_model_Placeholder",
        output="PartitionedCall:0"
    )

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        cur.execute("SELECT title FROM segments WHERE genre IS NULL OR genre = ''")
        to_process_titles = {row[0] for row in cur.fetchall()}

        all_wav_files = [f for f in os.listdir(segments_folder) if f.lower().endswith('.wav')]
        target_files = [f for f in all_wav_files if os.path.splitext(f)[0] in to_process_titles]

        print(f"Total segments: {len(all_wav_files)}")
        print(f"Segments to process: {len(target_files)}")

        if not target_files:
            print("All segments have already been processed.")
            return

        updated_count = 0
        for i, filename in enumerate(target_files, 1):
            title = os.path.splitext(filename)[0]
            full_path = os.path.join(segments_folder, filename)

            try:
                audio = es.MonoLoader(filename=full_path, sampleRate=16000)()
                embeddings = embedding_alg(audio)
                predictions = classification_alg(embeddings)

                mean_probs = np.mean(predictions, axis=0)
                mean_probs = np.exp(mean_probs) / np.sum(np.exp(mean_probs))
                top_indices = np.argsort(mean_probs)[-3:][::-1]
                genre = ", ".join([labels[j] for j in top_indices])

                cur.execute(
                    "UPDATE segments SET genre = %s WHERE title = %s",
                    (genre, title)
                )

                updated_count += 1
                if updated_count % 10 == 0:
                    conn.commit()

                print(f"[{i}/{len(target_files)}] {title} -> {genre.split(',')[0]}...")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

        conn.commit()
        print(f"Successfully updated genre for {updated_count} segments.")

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn is not None:
            cur.close()
            conn.close()

if __name__ == "__main__":
    update_genres()