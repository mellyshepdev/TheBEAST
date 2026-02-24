import os
import shutil
import psutil
import time
import argparse
import requests
from datetime import datetime, timedelta

# Configuration
THRESHOLD_PERCENT = 85.0
LARGE_FILE_SIZE_MB = 500
OLD_FILE_DAYS = 30
PROTECTED_DIRS = ["/etc", "/bin", "/usr", "/System32", ".git", ".vercel", "node_modules", "agent.skills"]
N8N_UPLOAD_WEBHOOK = os.environ.get("N8N_UPLOAD_WEBHOOK", "http://localhost:5678/webhook/Beast-Cloud-Upload")
N8N_ALERT_WEBHOOK = os.environ.get("N8N_ALERT_WEBHOOK", "http://localhost:5678/webhook/Beast-Disk-Alert")

def send_n8n_alert(percent, free_gb, candidates):
    """Send a disk pressure alert to n8n."""
    print(f"Sending disk alert to n8n...")
    try:
        payload = {
            "percent": percent,
            "free_gb": free_gb,
            "candidate_count": len(candidates),
            "top_candidates": [c['path'] for c in candidates[:5]],
            "beast_action": "disk_alert",
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(N8N_ALERT_WEBHOOK, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send n8n alert: {e}")
        return False

def get_disk_usage(path="."):
    usage = psutil.disk_usage(path)
    return usage.percent, usage.free / (1024**3)

def is_protected(path):
    for protected in PROTECTED_DIRS:
        if protected in path:
            return True
    return False

def find_offload_candidates(directory, size_mb=LARGE_FILE_SIZE_MB, days=OLD_FILE_DAYS):
    candidates = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for root, dirs, files in os.walk(directory):
        if is_protected(root):
            continue
            
        for name in files:
            filepath = os.path.join(root, name)
            try:
                stat = os.stat(filepath)
                size = stat.st_size / (1024**2)
                mtime = datetime.fromtimestamp(stat.st_mtime)
                
                if size > size_mb or mtime < cutoff_date:
                    candidates.append({
                        "path": filepath,
                        "size_mb": size,
                        "last_modified": mtime
                    })
            except Exception as e:
                pass
                
    return sorted(candidates, key=lambda x: x['size_mb'], reverse=True)

import hashlib

def calculate_checksum(filepath):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def offload_file(candidate, provider="google", target_dir=None):
    if target_dir:
        print(f"Moving {candidate['path']} to {target_dir}...")
        try:
            filename = os.path.basename(candidate['path'])
            destination = os.path.join(target_dir, filename)
            
            # Ensure target directory exists
            os.makedirs(target_dir, exist_ok=True)
            
            # Verify checksum before move for record
            local_checksum = calculate_checksum(candidate['path'])
            
            # Move file
            shutil.move(candidate['path'], destination)
            print(f"Success! Moved to: {destination}")
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False

    print(f"Offloading {candidate['path']} to {provider} via n8n strike...")
    try:
        local_checksum = calculate_checksum(candidate['path'])
        
        # Prepare file for upload
        with open(candidate['path'], 'rb') as f:
            files = {'file': (os.path.basename(candidate['path']), f)}
            data = {
                "path": candidate['path'],
                "size_mb": candidate['size_mb'],
                "provider": provider,
                "checksum": local_checksum,
                "beast_action": "offload_strike",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(N8N_UPLOAD_WEBHOOK, data=data, files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            cloud_url = result.get('url')
            remote_checksum = result.get('checksum')
            
            print(f"Success! Cloud URL: {cloud_url}")
            
            # Verify integrity if n8n returns a checksum
            if remote_checksum and remote_checksum == local_checksum:
                print("Integrity Verified. Removing local node copy...")
                # os.remove(candidate['path']) # Safety: keep commented until user confirms
                return True
            elif remote_checksum:
                print(f"❌ INTEGRITY FAILURE: Local {local_checksum} != Remote {remote_checksum}")
                return False
            else:
                print("Warning: Remote node did not return checksum for verification.")
                return True
        else:
            print(f"Failed to offload {candidate['path']}: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error during offload: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="The Beast Storage Manager")
    parser.add_argument("--dry-run", action="store_true", help="Don't perform any actions, just list candidates")
    parser.add_argument("--path", default=".", help="Base path to scan")
    parser.add_argument("--execute", action="store_true", help="Perform actual offloading (Requires n8n)")
    parser.add_argument("--provider", default="google", choices=["google", "onedrive"], help="Target cloud provider")
    parser.add_argument("--move-to", help="Directly move files to this local path (e.g. G:\\My Drive\\Offload)")
    args = parser.parse_args()

    percent, free_gb = get_disk_usage(args.path)
    print(f"Current Disk Usage: {percent}% ({free_gb:.2f} GB free)")

    if percent > THRESHOLD_PERCENT or args.dry_run:
        print(f"Disk pressure detected (Threshold: {THRESHOLD_PERCENT}%)")
        print("Scanning for offload candidates...")
        candidates = find_offload_candidates(args.path)
        
        # Trigger n8n alert
        if not args.dry_run:
            send_n8n_alert(percent, free_gb, candidates)
        
        if not candidates:
            print("No candidates found.")
            return

        print(f"Found {len(candidates)} candidates:")
        for c in candidates[:10]:
            print(f"- {c['path']} ({c['size_mb']:.2f} MB, Last Modified: {c['last_modified']})")

        if (args.execute or args.move_to) and not args.dry_run:
            target_desc = args.move_to if args.move_to else args.provider
            print(f"\nProceeding with offload of {len(candidates)} files to {target_desc}...")
            success_count = 0
            for c in candidates:
                if offload_file(c, provider=args.provider, target_dir=args.move_to):
                    success_count += 1
            print(f"\nCompleted. Successfully offloaded {success_count}/{len(candidates)} files.")
        elif args.dry_run:
            print("\n[DRY RUN] Run with --execute to perform the move.")
    else:
        print("Disk space within healthy limits.")

if __name__ == "__main__":
    main()
