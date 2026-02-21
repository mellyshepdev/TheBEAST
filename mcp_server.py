import asyncio
import os
import subprocess
from typing import Any, Dict, List, Optional
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server.stdio import stdio_server

# Create a server instance
server = Server("the-beast-server")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="run_scout",
            description="Run Trend Scout to discover viral pet content trends.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dry_run": {"type": "boolean", "description": "Run without API calls"}
                },
            },
        ),
        types.Tool(
            name="run_seo",
            description="Run SEO Monitor for a specific URL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to monitor"},
                    "save": {"type": "boolean", "description": "Save results to disk"}
                },
                "required": ["url"]
            },
        ),
        types.Tool(
            name="run_storage",
            description="Run Storage Manager to clean up disk space.",
            inputSchema={
                "type": "object",
                "properties": {
                    "execute": {"type": "boolean", "description": "Actually move files if true"}
                },
            },
        ),
        types.Tool(
            name="post_content",
            description="Post content to Instagram/TikTok using today's suggestion.",
            inputSchema={
                "type": "object",
                "properties": {
                    "media_path": {"type": "string", "description": "Path to the media file"},
                    "platform": {"type": "string", "enum": ["instagram", "tiktok", "all"]},
                    "dry_run": {"type": "boolean"}
                },
                "required": ["media_path"]
            },
        ),
        types.Tool(
            name="email_automation",
            description="Run automatic email cleanup or extraction for Gmail/Outlook.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["junk", "store", "all"]},
                    "account": {"type": "string", "enum": ["gmail", "outlook"]}
                },
                "required": ["action"]
            },
        )

    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any] | None
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}

    try:
        if name == "run_scout":
            cmd = ["python", "trend_scout.py", "--save"]
            if arguments.get("dry_run"):
                cmd.append("--dry-run")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [types.TextContent(type="text", text=f"Scout completed.\n{result.stdout}")]

        elif name == "run_seo":
            url = arguments.get("url")
            cmd = ["python", "seo_monitor.py", "--url", url]
            if arguments.get("save"):
                cmd.append("--save")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [types.TextContent(type="text", text=f"SEO Monitor for {url} completed.\n{result.stdout}")]

        elif name == "run_storage":
            cmd = ["python", "storage_manager.py"]
            if arguments.get("execute"):
                cmd.append("--execute")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [types.TextContent(type="text", text=f"Storage Manager completed.\n{result.stdout}")]

        elif name == "post_content":
            media = arguments.get("media_path")
            platform = arguments.get("platform", "instagram")
            cmd = ["python", "content_poster.py", "--media", media, "--platform", platform, "--from-suggestion"]
            if arguments.get("dry_run"):
                cmd.append("--dry-run")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [types.TextContent(type="text", text=f"Post task initiated.\n{result.stdout}")]

        elif name == "email_automation":
            action = arguments.get("action", "all")
            account = arguments.get("account", "gmail")
            cmd = ["python", "email_automation.py", "--action", action, "--account", account]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [types.TextContent(type="text", text=f"Email automation ({action}) completed.\n{result.stdout}")]


        else:
            raise ValueError(f"Unknown tool: {name}")

    except subprocess.CalledProcessError as e:
        return [types.TextContent(type="text", text=f"Error running {name}: {e.stderr or str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"An unexpected error occurred: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="the-beast-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
