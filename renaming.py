import os

def rename_songs():
    songs_dir = os.path.join(os.getcwd(), 'songs')

    files = [f for f in os.listdir(songs_dir) if os.path.isfile(os.path.join(songs_dir, f))]

    count = 0
    for filename in files:
        old_path = os.path.join(songs_dir, filename)

        name, ext = os.path.splitext(filename)

        new_name = name.replace(' ', '_')
        new_filename = new_name + ext

        new_path = os.path.join(songs_dir, new_filename)

        if old_path != new_path:
            if os.path.exists(new_path):
                print(f"Warning: Cannot rename '{filename}' to '{new_filename}', file already exists.")
            else:
                os.rename(old_path, new_path)
                print(f"Renamed: '{filename}' -> '{new_filename}'")
                count += 1

    print(f"Completed! Total {count} files renamed.")

if __name__ == "__main__":
    rename_songs()