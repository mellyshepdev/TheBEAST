import os
import shutil
import hashlib
import sys

def get_checksum(filename):
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def strike(source, destination_dir):
    if not os.path.exists(source):
        print(f"[SKIPPED] Source not found: {source}")
        return False
    
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir, exist_ok=True)
    
    filename = os.path.basename(source)
    dest = os.path.join(destination_dir, filename)
    
    print(f"[STRIKE] Moving {filename} -> {destination_dir}")
    
    try:
        source_hash = get_checksum(source)
        shutil.copy2(source, dest)
        dest_hash = get_checksum(dest)
        
        if source_hash == dest_hash:
            os.remove(source)
            print(f"[SUCCESS] {filename} moved and verified.")
            return True
        else:
            print(f"[ERROR] Hash mismatch for {filename}! Aborting deletion.")
            if os.path.exists(dest):
                os.remove(dest)
            return False
    except Exception as e:
        print(f"[FAILED] Error moving {filename}: {e}")
        return False

if __name__ == "__main__":
    targets = [
        r"C:\Users\Georg\OneDrive\Pictures\SD Card 1\20250128_143721.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card 1\20240412_105340.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card\videos\Downloading\Photos.zip",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card\videos\Downloading\Photos\Photos.zip",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card\videos\20241215_120945.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\Camera Roll\VID_20250902_174701.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card\videos\20250913_071345.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card 1\20210722_135103.mp4"
    ]
    
    dest_path = r"D:\Beast_Offload"
    
    success_count = 0
    for target in targets:
        if strike(target, dest_path):
            success_count += 1
            
    print(f"\n[STRIKE COMPLETE] Leon recovered {success_count} targets.")
