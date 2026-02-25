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
ANYTHING_LLM_API_KEY = os.environ.get("ANYTHING_LLM_API_KEY", "")
ANYTHING_LLM_URL = os.environ.get("ANYTHING_LLM_URL", "http://localhost:3001/api/v1")
N8N_INGEST_WEBHOOK = os.environ.get("N8N_INGEST_WEBHOOK", "http://localhost:5678/webhook/Beast-Cloud-Ingest")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

def get_embedding(text):
    """Generate embedding using OpenAI text-embedding-3-small."""
    if not OPENAI_KEY:
        return None
    try:
        # Truncate text to avoid token limits (approx 8k tokens)
        text = text[:32000].replace("\n", " ")
        resp = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            json={"input": text, "model": "text-embedding-3-small"},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"Embedding failed: {e}")
        return None

def send_to_n8n(file_data):
    """Notify n8n of a new ingested file."""
    print(f"Notifying n8n of ingestion: {file_data.get('path')}...")
    try:
        payload = {
            "file": file_data,
            "beast_action": "brain_ingest",
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(N8N_INGEST_WEBHOOK, json=payload, timeout=20)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to notify n8n: {e}")
        return False
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
            
            # ── Embedding Strike ────────────────────────────────────────────────
            embedding = None
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if content.strip():
                        embedding = get_embedding(content)
            except:
                pass
            
            if embedding:
                payload["embedding"] = embedding
            
            # Fallback for user_id to avoid RLS/FK constraint failures during initial setup
            # In a production context, this would be the actual auth.uid()
            payload["user_id"] = os.environ.get("STRIKE_USER_ID", "00000000-0000-0000-0000-000000000000")

            # Use Service Role Key to bypass RLS for initial ingestion
            headers = {**self.headers, "Authorization": f"Bearer {os.environ.get('SUPABASE_SERVICE_ROLE_KEY')}"}
            
            resp = requests.post(self.api_url, headers=headers, json=payload)
            resp.raise_for_status()
            
            # ── AnythingLLM Integration ──────────────────────────────────────────
            if ANYTHING_LLM_API_KEY:
                print(f"🧠 [VECTOR] Indexing {os.path.basename(filepath)} in AnythingLLM...")
                # Stub for AnythingLLM indexing - would typically involve uploading the file/text
                # to their workspace threads or document process.
                # requests.post(f"{ANYTHING_LLM_URL}/document/process", headers={"Authorization": f"Bearer {ANYTHING_LLM_API_KEY}"}, json=payload)

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
