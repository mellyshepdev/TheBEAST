from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import json
import asyncio

app = FastAPI(title="The Beast - Hands API")

# Allow the portal chatbot to call this API from any origin (browser CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to our scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = {
    "scout": os.path.join(BASE_DIR, "trend_scout.py"),
    "seo": os.path.join(BASE_DIR, "seo_monitor.py"),
    "storage": os.path.join(BASE_DIR, "storage_manager.py"),
    "health": os.path.join(BASE_DIR, "self_healing.py"),
    "loki": os.path.join(BASE_DIR, "loki_mode.py")
}

@app.get("/")
async def root():
    return {"status": "online", "message": "The Beast Hands are ready to strike."}

@app.post("/scout")
async def run_scout(background_tasks: BackgroundTasks):
    background_tasks.add_task(subprocess.run, ["python", SCRIPTS["scout"], "--save"])
    return {"message": "Trend Scout started in background."}

@app.post("/seo")
async def run_seo(background_tasks: BackgroundTasks, url: str = None):
    cmd = ["python", SCRIPTS["seo"], "--save"]
    if url:
        cmd.extend(["--url", url])
    background_tasks.add_task(subprocess.run, cmd)
    return {"message": f"SEO Monitor started for {url or 'default'} in background."}

@app.post("/storage")
async def run_storage(background_tasks: BackgroundTasks, execute: bool = False):
    cmd = ["python", SCRIPTS["storage"]]
    if execute:
        cmd.append("--execute")
    background_tasks.add_task(subprocess.run, cmd)
    return {"message": f"Storage Manager started (execute={execute}) in background."}

@app.post("/health")
async def run_health(background_tasks: BackgroundTasks):
    background_tasks.add_task(subprocess.run, ["python", SCRIPTS["health"]])
    return {"message": "System health check and self-healing cycle initiated."}

@app.post("/loki")
async def run_loki(background_tasks: BackgroundTasks):
    background_tasks.add_task(subprocess.run, ["python", SCRIPTS["loki"]])
    return {"message": "Loki Mode autonomous verification initiated."}

from mcp_coordinator import coordinator

@app.on_event("startup")
async def startup_event():
    # Connect to configured MCP servers on startup
    asyncio.create_task(coordinator.connect_all())

@app.get("/mcp/tools")
async def list_mcp_tools():
    return await coordinator.list_tools()

@app.post("/mcp/call")
async def call_mcp_tool(request: dict):
    server = request.get("server")
    tool = request.get("tool")
    arguments = request.get("arguments", {})
    result = await coordinator.call_tool(server, tool, arguments)
    return {"result": result}

from tone_mirror import mirror

@app.post("/chat")
async def beast_chat(message: dict):
    user_msg = message.get("text", "")
    sentiment = mirror.analyze(user_msg)
    prefix = mirror.get_response_style(sentiment)
    
    user_msg_low = user_msg.lower()
    
    # Logic for status and actions
    if "status" in user_msg_low:
        response = f"{prefix}\nTHE BEAST STATUS: ALL SYSTEMS GO. HANDS ARE READY."
    elif "scout" in user_msg_low:
        response = f"{prefix}\nTREND SCOUT IS ON STANDBY. USE /scout TO STRIKE."
    else:
        response = f"{prefix}\nI AM THE BEAST. SYSTEM PARITY MAINTAINED."
        
    return {"reply": response, "sentiment": sentiment}
