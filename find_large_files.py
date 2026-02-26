import os

def find_large_files_ext(start_path, extensions=None, limit=20):
    if extensions is None:
        extensions = ['.iso', '.zip', '.exe', '.mp4', '.msi', '.rar', '.7z', '.mov', '.vmdk', '.ova']
    
    print(f"Surgical Scan for {extensions} in {start_path}...")
    large_files = []
    
    # Folders to skip
    skip_dirs = ['System32', 'Windows', 'Program Files', 'Program Files (x86)', '.git', 'node_modules', '.venv', 'AppData', 'OneDrive']
    
    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in files:
            if any(name.lower().endswith(ext) for ext in extensions):
                filepath = os.path.join(root, name)
                try:
                    size_bytes = os.path.getsize(filepath)
                    if size_bytes > 5 * 1024 * 1024: # > 5MB
                        large_files.append((size_bytes, filepath))
                except:
                    pass
            
    large_files.sort(key=lambda x: x[0], reverse=True)
    return large_files[:limit]

if __name__ == "__main__":
    home = os.path.expanduser("~")
    results = find_large_files_ext(home, limit=10)
    print("\n--- SURGICAL STRIKE LIST (TOP 10) ---")
    for size_bytes, path in results:
        size_mb = size_bytes / (1024 * 1024)
        print(f"{size_mb:.2f} MB | {path}")
