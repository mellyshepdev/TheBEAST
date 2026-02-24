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
        """Checks status of essential Docker containers via MCP."""
        print("[HEALTH] Checking remote containers via Docker MCP...")
        try:
            # Attempt to list containers via the docker MCP server
            resp = await self.coordinator.call_tool("docker", "list_containers", {})
            containers = resp.content if hasattr(resp, 'content') else []
            
            # Filter for essential services (e.g., ELK, Synapse)
            critical_services = ["elk", "elasticsearch", "logstash", "kibana", "synapse"]
            status_report = []
            
            # Simple simulation of status check from list results
            # In a real MCP response, we'd parse the JSON/List
            print(f"[HEALTH] Received data for {len(containers)} containers.")
            
            # Check for stopped critical services
            # This is a bit speculative on the structure of mcp-server-docker output, 
            # but usually it returns a string or list of objects.
            container_str = str(containers).lower()
            for service in critical_services:
                if service in container_str:
                    if "exited" in container_str or "stopped" in container_str:
                        await self.alert(f"⚠️ CRITICAL SERVICE DOWN: {service.upper()} is not running!")
                        status_report.append({"service": service, "status": "down"})
                    else:
                        status_report.append({"service": service, "status": "running"})
            
            return {"status": "ok", "checks": status_report}
        except Exception as e:
            print(f"[WARN] Docker MCP check failed: {e}")
            # Fallback to local check or pending status
            return {"status": "error", "message": str(e)}

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
