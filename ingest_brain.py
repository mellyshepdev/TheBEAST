import os
import sys
import argparse
import json
import uuid
import requests
from datetime import datetime

# Force UTF-8 output for Windows terminals to support emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
PROTECTED_DIRS = [".git", ".vercel", "node_modules", "agent.skills", "__pycache__", ".agent", ".idx"]
TEXT_EXTENSIONS = [".txt", ".md", ".py", ".html", ".css", ".js", ".json", ".toml", ".yml", ".yaml"]

class BrainIngester:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.api_url = f"{SUPABASE_URL}/rest/v1/cloud_files"
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

    def is_protected(self, path):
        for protected in PROTECTED_DIRS:
            if protected in path:
                return True
        return False

    def ingest_directory(self, directory):
        print(f"🧠 [BRAIN] Ingesting directory: {directory}")
        count = 0
        for root, dirs, files in os.walk(directory):
            if self.is_protected(root):
                continue

            for name in files:
                ext = os.path.splitext(name)[1].lower()
                if ext in TEXT_EXTENSIONS:
                    filepath = os.path.join(root, name)
                    self.ingest_file(filepath)
                    count += 1
        print(f"🧠 [BRAIN] Ingestion complete. {count} files processed.")

    def ingest_file(self, filepath):
        try:
            stat = os.stat(filepath)
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # For now, we don't store full content in the metadata DB for large files
            # but we record where the file is.
            payload = {
                "file_name": os.path.basename(filepath),
                "provider": "local",
                "remote_id": os.path.abspath(filepath),
                "mime_type": f"text/plain", # simplified
                "size": size,
                "metadata": {
                    "path": os.path.abspath(filepath),
                    "last_modified": mtime,
                    "ingested_at": datetime.utcnow().isoformat()
                }
            }

            if self.dry_run:
                print(f"[DRY RUN] Would ingest: {os.path.basename(filepath)} ({size} bytes)")
                return

            # Note: We need a valid USER_ID if RLS is enabled. 
            # In a local dev context without a logged-in session, we might need a service role key 
            # or temporary relax RLS for the initial ingestion.
            # For this MVP, we assume the user has configured Supabase correctly.
            
            # Since we don't have a user_id here, this might fail unless RLS is bypassable 
            # with a service role. If it fails, we log it.
            # payload["user_id"] = "YOUR_STUB_USER_ID" 

            print(f"[LIVE] Ingesting: {os.path.basename(filepath)}...")
            # Uncomment below once SUPABASE_URL and SUPABASE_KEY are real and user_id is handled
            # resp = requests.post(self.api_url, headers=self.headers, json=payload)
            # resp.raise_for_status()

        except Exception as e:
            print(f"[ERROR] Failed to process {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="The Beast Brain Ingester")
    parser.add_argument("--path", default=".", help="Directory to index")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without DB calls")
    args = parser.parse_args()

    if not args.dry_run and (not SUPABASE_URL or "YOUR_SUPABASE" in SUPABASE_URL):
        print("[WARN] SUPABASE_URL not configured. Running in DRY RUN mode.")
        args.dry_run = True

    ingester = BrainIngester(dry_run=args.dry_run)
    ingester.ingest_directory(args.path)

if __name__ == "__main__":
    main()
