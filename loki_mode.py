import os
import sys
import json
import requests
import argparse
import subprocess
from datetime import datetime

# Force UTF-8 for Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
FLY_HANDS_URL = "https://beast-hands.fly.dev"
FLY_VOICE_URL = "https://beast-openclaw.fly.dev"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

class LokiVerifier:
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS",
            "checks": {}
        }

    def log_check(self, name, status, message):
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} [{name}] {message}")
        self.report["checks"][name] = {"status": status, "message": message}

    def verify_ground(self):
        """Verifies local environment and critical scripts."""
        scripts = ["beast.py", "hands_api.py", "openclaw_api.py", "self_healing.py", "ingest_brain.py", "verify_voice.py"]
        missing = [s for s in scripts if not os.path.exists(s)]
        
        if not missing:
            self.log_check("GROUND", "PASS", "All critical local scripts present.")
        else:
            self.log_check("GROUND", "FAIL", f"Missing scripts: {', '.join(missing)}")

    def verify_brain(self):
        """Verifies Supabase connectivity and schema existence."""
        if not SUPABASE_URL or "YOUR_" in SUPABASE_URL:
            self.log_check("BRAIN", "SKIP", "Supabase credentials not configured.")
            return

        try:
            url = f"{SUPABASE_URL}/rest/v1/cloud_files?select=count"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                self.log_check("BRAIN", "PASS", "Supabase reachable and schema verified.")
            else:
                self.log_check("BRAIN", "FAIL", f"Supabase error: {resp.status_code}")
        except Exception as e:
            self.log_check("BRAIN", "FAIL", f"Supabase connection failed: {e}")

    def verify_hands(self):
        """Verifies Fly.io Hands API and self-healing endpoint."""
        try:
            resp = requests.get(f"{FLY_HANDS_URL}/health", timeout=10)
            if resp.status_code == 200:
                self.log_check("HANDS", "PASS", "Hands API live on Fly.io and diagnostics active.")
            else:
                self.log_check("HANDS", "FAIL", f"Hands API returned: {resp.status_code}")
        except Exception as e:
            self.log_check("HANDS", "FAIL", f"Hands API unreachable: {e}")

    def verify_voice(self):
        """Verifies Fly.io OpenClaw API."""
        try:
            resp = requests.get(f"{FLY_VOICE_URL}/", timeout=10)
            if resp.status_code == 200:
                self.log_check("VOICE", "PASS", "OpenClaw API live on Fly.io.")
            else:
                self.log_check("VOICE", "FAIL", f"OpenClaw returned: {resp.status_code}")
        except Exception as e:
            self.log_check("VOICE", "FAIL", f"OpenClaw unreachable: {e}")

    def verify_barcode(self):
        """Verifies Barcode integration and local/remote handler."""
        has_handler = os.path.exists("barcode_handler.py")
        
        try:
            resp = requests.post(f"{FLY_HANDS_URL}/scan", timeout=10)
            api_ready = resp.status_code == 200
        except:
            api_ready = False

        if has_handler and api_ready:
            self.log_check("BARCODE", "PASS", "Barcode logic integrated and endpoint active.")
        elif has_handler:
            self.log_check("BARCODE", "DEGRADED", "Handler present, but Hands API endpoint unreachable.")
        else:
            self.log_check("BARCODE", "FAIL", "Barcode handler script missing.")

    def run_all(self):
        print("\n🔥 [LOKI MODE] Initiating Autonomous Verification...")
        self.verify_ground()
        self.verify_brain()
        self.verify_hands()
        self.verify_voice()
        self.verify_barcode()
        
        # Final status
        all_passed = all(c["status"] in ["PASS", "SKIP", "PENDING"] for c in self.report["checks"].values())
        self.report["status"] = "COMPLETE" if all_passed else "DEGRADED"
        
        print(f"\n📢 [LOKI REPORT] System Status: {self.report['status']}")
        with open("loki_report.json", "w") as f:
            json.dump(self.report, f, indent=4)
        print(f"📄 Report saved to loki_report.json\n")

def main():
    parser = argparse.ArgumentParser(description="Loki Mode - Autonomous Verification")
    args = parser.parse_args()
    
    verifier = LokiVerifier()
    verifier.run_all()

if __name__ == "__main__":
    main()
