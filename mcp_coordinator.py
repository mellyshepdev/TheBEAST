import asyncio
import json
import os
from typing import Dict, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPCoordinator:
    def __init__(self, config_path: str = "mcp_config.json"):
        self.config_path = config_path
        self.sessions: Dict[str, ClientSession] = {}
        self.server_params: Dict[str, StdioServerParameters] = {}

    async def load_config(self):
        if not os.path.exists(self.config_path):
            print(f"[WARN] MCP config not found: {self.config_path}")
            return

        with open(self.config_path, "r") as f:
            config = json.load(f)
            for name, server_config in config.get("mcpServers", {}).items():
                self.server_params[name] = StdioServerParameters(
                    command=server_config["command"],
                    args=server_config["args"],
                    env={**os.environ, **server_config.get("env", {})}
                )

    async def connect_all(self):
        await self.load_config()
        
        # Skip MCP connections if in a restricted container environment like Fly.io
        # unless explicitly required (since local paths/binaries won't exist)
        if os.getenv("FLY_APP_NAME"):
            print("[MCP] Cloud environment detected. Skipping local MCP connections.")
            return

        for name, params in self.server_params.items():
            print(f"[MCP] Connecting to {name}...")
            try:
                transport_ctx = stdio_client(params)
                read, write = await transport_ctx.__aenter__()
                session = ClientSession(read, write)
                await session.__aenter__()
                await session.initialize()
                self.sessions[name] = session
                print(f"[MCP] {name} connected.")
            except Exception as e:
                print(f"[WARN] Failed to connect to MCP server {name}: {e}")

    async def list_tools(self) -> Dict[str, List[Any]]:
        all_tools = {}
        for name, session in self.sessions.items():
            tools = await session.list_tools()
            all_tools[name] = tools.tools
        return all_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
        if server_name not in self.sessions:
            raise ValueError(f"Server {server_name} not connected.")
        return await self.sessions[server_name].call_tool(tool_name, arguments)

    async def shutdown(self):
        for name, session in self.sessions.items():
            await session.__aexit__(None, None, None)
        print("[MCP] Shutdown complete.")

coordinator = MCPCoordinator()
