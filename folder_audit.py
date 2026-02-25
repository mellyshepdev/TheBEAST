import os

def get_dir_size(path):
    total_size = 0
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                fp = os.path.join(root, file)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except Exception:
        pass
    return total_size

def find_top_folders(base_path, limit=10):
    print(f"Analyzing folders in {base_path}...")
    folders = []
    try:
        # Only look at immediate subdirectories to avoid deep recursion initially
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                size = get_dir_size(item_path)
                folders.append((size, item_path))
    except Exception as e:
        print(f"Error listing {base_path}: {e}")
        
    folders.sort(key=lambda x: x[0], reverse=True)
    return folders[:limit]

if __name__ == "__main__":
    base = os.path.expanduser("~")
    top_folders = find_top_folders(base)
    print("\n--- TOP FOLDERS BY SIZE ---")
    for size, path in top_folders:
        size_gb = size / (1024 * 1024 * 1024)
        print(f"{size_gb:.2f} GB | {path}")
