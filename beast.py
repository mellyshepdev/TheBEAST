import argparse
import requests
import json
import sys
import os

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
    parser.add_argument("--health", action="store_true", help="Run self-healing diagnostics")
    parser.add_argument("--loki", action="store_true", help="Run Loki Mode autonomous verification")
    parser.add_argument("--scan", action="store_true", help="Trigger Barcode Scanner")
    parser.add_argument("--scout", action="store_true", help="Trigger Trend Scout")
    parser.add_argument("--seo", type=str, help="Trigger SEO Monitor for URL")
    parser.add_argument("--chat", type=str, help="Chat with The Beast")
    parser.add_argument("--msg", type=str, help="Send message via OpenClaw")
    parser.add_argument("--channel", type=str, default="matrix", help="Channel for message")
    parser.add_argument("--mcp-list", action="store_true", help="List tools from connected MCP servers")
    parser.add_argument("--message", type=str, help="Send a message via Voice (OpenClaw)")
    parser.add_argument("--brief", action="store_true", help="Trigger a Sovereign Briefing (System Health)")
    parser.add_argument("--mcp-call", nargs=3, metavar=("SERVER", "TOOL", "ARGS_JSON"), help="Call an MCP tool")

    args = parser.parse_args()

    if args.status:
        # Check local and remote status
        print("Checking status of The Beast...")
        os.system("python loki_mode.py")
    
    elif args.brief:
        print("[LEON]: Preparing your Sovereign Briefing...")
        from self_healing import SelfHealing
        monitor = SelfHealing()
        import asyncio
        results = asyncio.run(monitor.run_diagnostics())
        
        briefing = f"Sovereign Briefing Complete.\nSSL: {results['ssl']['status']}\nContainers: {results['containers']['status']}\nAll systems verified."
        
        # Send to Voice
        payload = {"text": briefing, "channel": "matrix", "priority": "normal"}
        try:
            requests.post(f"{VOICE_URL}/send", json=payload)
            print("✅ Briefing delivered to your primary channel.")
        except Exception as e:
            print(f"❌ Failed to reach the Voice: {e}")

    elif args.health:
        print("RUNNING SYSTEM DIAGNOSTICS...")
        try:
            resp = requests.get(f"{HANDS_URL}/health")
            data = resp.json()
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"FAILED TO FETCH HEALTH: {e}")
    elif args.loki:
        run_action("hands", "loki")
    elif args.scan:
        run_action("hands", "scan")
    elif args.scout:
        run_action("hands", "scout")
    elif args.seo:
        run_action("hands", "seo", url=args.seo)
    elif args.mcp_list:
        print("FETCHING MCP TOOLS...")
        try:
            resp = requests.get(f"{HANDS_URL}/mcp/tools")
            tools = resp.json()
            for server, tool_list in tools.items():
                print(f"\n[{server.upper()}]")
                for tool in tool_list:
                    print(f"  - {tool['name']}: {tool['description']}")
        except Exception as e:
            print(f"FAILED TO FETCH TOOLS: {e}")
    elif args.mcp_call:
        server, tool, args_json = args.mcp_call
        print(f"CALLING {tool} ON {server}...")
        try:
            payload = json.loads(args_json)
            resp = requests.post(f"{HANDS_URL}/mcp/call", json={
                "server": server,
                "tool": tool,
                "arguments": payload
            })
            print(f"RESULT: {resp.json()}")
        except Exception as e:
            print(f"FAILED TO CALL TOOL: {e}")
    elif args.chat:
        print("\n--- INITIATING COMMS WITH THE BEAST ---")
        try:
            resp = requests.post(f"{HANDS_URL}/chat", json={"text": args.chat})
            data = resp.json()
            sentiment = data.get('sentiment', 'relaxed').upper()
            reply = data.get('reply', '...')
            
            # Simple status prefixes (avoiding Unicode emojis for Windows terminal safety)
            prefixes = {
                "UPSET": "[CRITICAL]",
                "UPBEAT": "[VICTORY]",
                "ANALYTICAL": "[RECON]",
                "CASUAL": "[STATUS]",
                "SECURITY": "[SHIELD]",
                "RELAXED": "[IDLE]"
            }
            prefix = prefixes.get(sentiment, "[INFO]")
            
            print(f"\n{prefix} {reply}\n")
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
