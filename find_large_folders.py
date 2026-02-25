import os

def get_folder_size(folder):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except:
        pass
    return total_size

def find_large_folders(root_path, limit=10):
    print(f"Scanning {root_path} for top {limit} folders...")
    folders = []
    
    try:
        for entry in os.scandir(root_path):
            if entry.is_dir():
                size = get_folder_size(entry.path) / (1024 * 1024 * 1024) # Size in GB
                folders.append((size, entry.name))
    except:
        pass
            
    folders.sort(key=lambda x: x[0], reverse=True)
    return folders[:limit]

if __name__ == "__main__":
    home = os.path.expanduser("~")
    results = find_large_folders(home, limit=10)
    print("\n--- TOP FOLDER SIZES ---")
    for size_gb, name in results:
        print(f"{size_gb:.2f} GB | {name}")
