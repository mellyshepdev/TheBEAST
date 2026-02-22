import asyncio
import ssl
import socket
import datetime
import requests
import os
from mcp_coordinator import coordinator

# Configuration
MONITORED_DOMAIN = "theofficialblacksheepcompany.com"
SSL_THRESHOLD_DAYS = 7
VOICE_URL = "https://beast-openclaw.fly.dev/send"

class SelfHealing:
    def __init__(self):
        self.coordinator = coordinator

    async def check_ssl(self, domain: str):
        """Checks SSL certificate expiration date."""
        print(f"[HEALTH] Checking SSL for {domain}...")
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    expire_date_str = cert['notAfter']
                    expire_date = datetime.datetime.strptime(expire_date_str, '%b %d %H:%M:%S %Y %Z')
                    remaining = expire_date - datetime.datetime.utcnow()
                    
                    if remaining.days < SSL_THRESHOLD_DAYS:
                        await self.alert(f"⚠️ SSL WARNING: Certificate for {domain} expires in {remaining.days} days!")
                    else:
                        print(f"[HEALTH] SSL OK: {remaining.days} days remaining.")
                    return {"status": "ok", "days_remaining": remaining.days}
        except Exception as e:
            await self.alert(f"❌ SSL CRITICAL: Failed to check {domain}. Error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def check_containers(self):
        """Placeholder for monitoring Docker containers on remote nodes via MCP."""
        print("[HEALTH] Checking remote containers...")
        # In a full implementation, we'd call:
        # await self.coordinator.call_tool("docker", "list_containers", {})
        # Or run shell command on remote node:
        # await self.coordinator.call_tool("apple-system", "run_shell_command", {"command": "docker ps"})
        
        # For now, we simulate a check
        print("[HEALTH] Remote nodes verification pending MCP setup.")
        return {"status": "pending_mcp"}

    async def alert(self, message: str):
        """Sends an alert via OpenClaw."""
        print(f"[ALERT] {message}")
        try:
            payload = {
                "text": message,
                "channel": "matrix",
                "priority": "high"
            }
            # Note: OpenClaw might be local or remote. 
            # Using the configured URL from beast.py
            requests.post(VOICE_URL, json=payload)
        except Exception as e:
            print(f"[ERROR] Failed to send alert: {e}")

    async def run_diagnostics(self):
        """Runs all health checks."""
        try:
            await self.coordinator.connect_all()
        except Exception as e:
            print(f"[WARN] MCP Coordinator failed to connect: {e}")
            
        results = {}
        results["ssl"] = await self.check_ssl(MONITORED_DOMAIN)
        results["containers"] = await self.check_containers()
        
        try:
            await self.coordinator.shutdown()
        except:
            pass
            
        return results

if __name__ == "__main__":
    monitor = SelfHealing()
    asyncio.run(monitor.run_diagnostics())
