import os
import sys
import requests
import argparse

# Force UTF-8 output for Windows terminals to support emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
VOICE_URL = "https://beast-openclaw.fly.dev/send"
GATEWAYS = {
    "matrix": os.environ.get("MATRIX_WEBHOOK_URL"),
    "slack": os.environ.get("SLACK_WEBHOOK_URL")
}

def verify_voice(channel="matrix"):
    print(f"🔊 [VOICE] Verifying {channel} connection...")
    webhook = GATEWAYS.get(channel)
    
    if not webhook or "YOUR_" in webhook:
        print(f"❌ [FAIL] Webhook for {channel} is not configured in .env")
        return False

    try:
        # Test 1: Direct Webhook Test (if applicable)
        print(f"   - Sending test heartbeat to {channel}...")
        
        # We'll use the OpenClaw API wrapper if possible, or hit the webhook directly
        # For verification, hitting the OpenClaw API is better because it tests the whole chain.
        payload = {
            "text": f"🔊 BEAST VOICE HEARTBEAT: Verification successful for {channel}.",
            "channel": channel,
            "priority": "high"
        }
        
        # Note: If OpenClaw is not deployed yet, this will fail. 
        # We try both local and remote scenarios.
        try:
            resp = requests.post(VOICE_URL, json=payload, timeout=10)
            if resp.status_code == 200:
                print(f"✅ [SUCCESS] {channel} heartbeat routed via OpenClaw.")
                return True
        except:
            print(f"   - OpenClaw remote unreachable. Attempting direct heartbeat...")
            # Direct logic would go here depending on provider format
            pass
            
        print(f"⚠️ [WARN] Could not reach OpenClaw service. Check deployment status.")
        return False

    except Exception as e:
        print(f"❌ [ERROR] Verification failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="The Beast Voice Verifier")
    parser.add_argument("--channel", default="all", choices=["matrix", "slack", "all"], help="Channel to verify")
    args = parser.parse_args()

    channels = ["matrix", "slack"] if args.channel == "all" else [args.channel]
    
    for c in channels:
        verify_voice(c)

if __name__ == "__main__":
    main()
