from fastapi import FastAPI, BackgroundTasks
import os
import subprocess
import json

app = FastAPI(title="The Beast - Hands API")

# Path to our scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = {
    "scout": os.path.join(BASE_DIR, "trend_scout.py"),
    "seo": os.path.join(BASE_DIR, "seo_monitor.py"),
    "storage": os.path.join(BASE_DIR, "storage_manager.py")
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
