import subprocess
import os

def free_up_onedrive_space(file_list):
    print(f"Initiating Sovereign Freeze on {len(file_list)} targets...")
    success_count = 0
    
    for filepath in file_list:
        if not os.path.exists(filepath):
            continue
            
        print(f"[FREEZE] Targeting {os.path.basename(filepath)}")
        try:
            # attrib +U (On-demand) -P (Pinned off)
            # This triggers OneDrive to remove the local copy but keep the cloud reference
            subprocess.run(['attrib', '+U', '-P', filepath], check=True)
            print(f"[SUCCESS] {os.path.basename(filepath)} is now Online-only.")
            success_count += 1
        except Exception as e:
            print(f"[FAILED] Could not freeze {filepath}: {e}")
            
    return success_count

if __name__ == "__main__":
    # Top targets from onedrive_scan.py
    targets = [
        r"C:\Users\Georg\OneDrive\Pictures\SD Card 1\20250128_143721.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card 1\20240412_105340.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card\videos\Downloading\Photos.zip",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card\videos\Downloading\Photos\Photos.zip",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card\videos\20241215_120945.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\Camera Roll\VID_20250902_174701.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card\videos\20250913_071345.mp4",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card 1\20210722_135103.mp4",
        r"C:\Users\Georg\OneDrive\Apps\OllamaSetup.exe",
        r"C:\Users\Georg\OneDrive\Pictures\SD Card 1\VID_20230603_131425945.mp4"
    ]
    
    freed = free_up_onedrive_space(targets)
    print(f"\n[FREEZE COMPLETE] Leon triggered cloud-offload for {freed} files.")
