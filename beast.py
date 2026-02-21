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
    parser.add_argument("--health", action="store_true", help="Run self-healing diagnostics")
    parser.add_argument("--loki", action="store_true", help="Run Loki Mode autonomous verification")
    parser.add_argument("--scout", action="store_true", help="Trigger Trend Scout")
    parser.add_argument("--seo", type=str, help="Trigger SEO Monitor for URL")
    parser.add_argument("--chat", type=str, help="Chat with The Beast")
    parser.add_argument("--msg", type=str, help="Send message via OpenClaw")
    parser.add_argument("--channel", type=str, default="matrix", help="Channel for message")
    parser.add_argument("--mcp-list", action="store_true", help="List tools from connected MCP servers")
    parser.add_argument("--mcp-call", nargs=3, metavar=("SERVER", "TOOL", "ARGS_JSON"), help="Call an MCP tool")

    args = parser.parse_args()

    if args.status:
        get_status()
    elif args.health:
        run_action("hands", "health")
    elif args.loki:
        run_action("hands", "loki")
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
