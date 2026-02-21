import argparse
import requests
import json
import sys

HANDS_URL = "https://beast-hands.fly.dev"
VOICE_URL = "https://beast-openclaw.fly.dev"

def get_status():
    print("--- THE BEAST SYSTEM STATUS ---")
    try:
        hands = requests.get(HANDS_URL).json()
        print(f"HANDS (Automation): {hands.get('status', 'OFFLINE')} - {hands.get('message', '')}")
    except Exception as e:
        print(f"HANDS (Automation): OFFLINE ({e})")

    try:
        voice = requests.get(VOICE_URL).json()
        print(f"VOICE (Communication): {voice.get('status', 'OFFLINE')} - {voice.get('message', '')}")
    except Exception as e:
        print(f"VOICE (Communication): OFFLINE ({e})")

def run_action(target, action, **kwargs):
    url = f"{HANDS_URL}/{action}"
    print(f"STRIKING: {action} via {HANDS_URL}...")
    try:
        resp = requests.post(url, json=kwargs)
        print(resp.json().get("message", "Action initiated."))
    except Exception as e:
        print(f"FAILED TO STRIKE: {e}")

def main():
    parser = argparse.ArgumentParser(description="THE BEAST - Universal CLI Control")
    parser.add_argument("--status", action="store_true", help="Check system health")
    parser.add_argument("--scout", action="store_true", help="Trigger Trend Scout")
    parser.add_argument("--seo", type=str, help="Trigger SEO Monitor for URL")
    parser.add_argument("--chat", type=str, help="Chat with The Beast")
    parser.add_argument("--msg", type=str, help="Send message via OpenClaw")
    parser.add_argument("--channel", type=str, default="matrix", help="Channel for message")

    args = parser.parse_args()

    if args.status:
        get_status()
    elif args.scout:
        run_action("hands", "scout")
    elif args.seo:
        run_action("hands", "seo", url=args.seo)
    elif args.chat:
        print("TALKING TO THE BEAST...")
        try:
            resp = requests.post(f"{HANDS_URL}/chat", json={"text": args.chat})
            data = resp.json()
            print(f"[{data.get('sentiment', 'RELAXED').upper()}] {data.get('reply')}")
        except Exception as e:
            print(f"FAILED TO CHAT: {e}")
    elif args.msg:
        print(f"VOICING: Sending message to {args.channel}...")
        try:
            resp = requests.post(f"{VOICE_URL}/send", json={"text": args.msg, "channel": args.channel})
            print(resp.json().get("status", "Sent."))
        except Exception as e:
            print(f"FAILED TO VOICE: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
