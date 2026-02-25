from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import os
import logging
from tone_mirror import mirror

app = FastAPI(title="OpenClaw - The Voice of the Beast")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message(BaseModel):
    text: str
    channel: str = "matrix"  # default channel
    recipient: str = None
    priority: str = "normal"

# Gateway Configurations (to be moved to env vars)
GATEWAYS = {
    "matrix": os.getenv("MATRIX_WEBHOOK_URL"),
    "slack": os.getenv("SLACK_WEBHOOK_URL"),
    "whatsapp": os.getenv("WHATSAPP_API_URL")
}

@app.get("/")
async def root():
    return {"status": "online", "message": "OpenClaw is listening. The Voice is active."}

@app.post("/send")
async def send_message(msg: Message, request: Request):
    # Inject Leon's Persona with Tone Mirroring
    sentiment, intensity = mirror.analyze(msg.text)
    style_instruction = mirror.get_style_instruction(sentiment, intensity)
    
    leon_prefix = f"🧤 [LEON - {sentiment.upper()}]: "
    if msg.priority == "high":
        leon_prefix = "🚨 [SYSTEM CRITICAL - LEON]: "
    
    # In OpenClaw, we use the style_instruction as a footer for system-generated messages
    formatted_text = f"{leon_prefix}{msg.text}\n\n_{style_instruction}_"
    logger.info(f"Routing message to {msg.channel}: {formatted_text[:50]}...")
    
    url = GATEWAYS.get(msg.channel.lower())
    if not url:
        raise HTTPException(status_code=400, detail=f"Gateway for {msg.channel} not configured.")

    token = os.getenv(f"{msg.channel.upper()}_TOKEN")
    auth_header = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        async with httpx.AsyncClient() as client:
            if msg.channel.lower() == "slack":
                payload = {
                    "text": f"*BEAST NOTIFICATION* [{msg.priority.upper()}]\n{formatted_text}",
                    "username": "LEON AI - THE BEAST",
                    "icon_emoji": ":robot_face:"
                }
                response = await client.post(url, json=payload)
            
            elif msg.channel.lower() == "matrix":
                payload = {
                    "msgtype": "m.text",
                    "body": formatted_text,
                    "format": "org.matrix.custom.html",
                    "formatted_body": f"<strong>LEON</strong>: {msg.text}"
                }
                response = await client.post(url, json=payload, headers=auth_header)
            
            elif msg.channel.lower() == "whatsapp":
                # Standard WhatsApp/n8n broadcast format
                payload = {
                    "message": formatted_text,
                    "phone": msg.recipient or os.getenv("OWNER_PHONE"),
                    "sender": "Leon AI"
                }
                response = await client.post(url, json=payload)
            
            else:
                payload = {"message": formatted_text, "sender": "Leon AI"}
                response = await client.post(url, json=payload)
                
            response.raise_for_status()
            
        return {"status": "success", "channel": msg.channel, "provider_status": response.status_code}
    except Exception as e:
        logger.error(f"Failed to route message to {msg.channel}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Handshake failed: {str(e)}")

@app.post("/broadcast")
async def broadcast_message(msg: Message):
    """Sends a message to ALL configured gateways."""
    logger.info(f"Initiating Global Broadcast: {msg.text[:50]}...")
    results = {}
    
    for channel in GATEWAYS.keys():
        if GATEWAYS[channel]:
            try:
                # Reuse send_message logic internally or via helper
                # For simplicity, we just iterate here
                msg.channel = channel
                res = await send_message(msg, None)
                results[channel] = "sent"
            except Exception as e:
                results[channel] = f"failed: {str(e)}"
    
    return {"status": "broadcast_complete", "results": results}

@app.post("/slack/webhook")
async def slack_webhook(request: Request):
    """Handles incoming Slack events/messages."""
    form_data = await request.form()
    # Slack slash commands send data as form-urlencoded
    user_text = form_data.get("text", "")
    user_id = form_data.get("user_id", "unknown")
    
    logger.info(f"Received Slack command from {user_id}: {user_text}")
    
    # Forward to Hands API (Leon's brain)
    HANDS_URL = os.getenv("HANDS_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{HANDS_URL}/chat", json={"text": user_text})
            data = resp.json()
            return {"text": data.get("reply", "Leon is processing...")}
    except Exception as e:
        logger.error(f"Failed to reach Hands API: {e}")
        return {"text": "⚠️ Communication with Leon's core is offline."}

@app.get("/health")
async def health():
    return {"status": "healthy", "gateways": [k for k, v in GATEWAYS.items() if v]}
