import os

def find_large_onedrive_files(start_path, min_size_mb=50, limit=10):
    print(f"Scanning {start_path} for large local files...")
    large_files = []
    
    for root, dirs, files in os.walk(start_path):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                # In Windows, we can check if a file is local or virtual
                # For this script, we'll look for files > 50MB and assume
                # the user can tell us if they are local.
                size_bytes = os.path.getsize(filepath)
                size_mb = size_bytes / (1024 * 1024)
                if size_mb > min_size_mb:
                    large_files.append((size_mb, filepath))
            except:
                pass
    
    large_files.sort(key=lambda x: x[0], reverse=True)
    return large_files[:limit]

if __name__ == "__main__":
    onedrive = r"C:\Users\Georg\OneDrive"
    results = find_large_onedrive_files(onedrive)
    print("\n--- ONEDRIVE HIT-LIST ---")
    for size, path in results:
        print(f"{size:.2f} MB | {path}")
