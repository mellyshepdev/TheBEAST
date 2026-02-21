from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import os
import logging

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
    logger.info(f"Routing message to {msg.channel}: {msg.text[:50]}...")
    
    url = GATEWAYS.get(msg.channel.lower())
    if not url:
        raise HTTPException(status_code=400, detail=f"Gateway for {msg.channel} not configured.")

    # Extract optional auth from environment or header
    token = os.getenv(f"{msg.channel.upper()}_TOKEN")
    auth_header = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        async with httpx.AsyncClient() as client:
            if msg.channel.lower() == "slack":
                # Slack Webhook format
                payload = {
                    "text": f"*BEAST NOTIFICATION* [{msg.priority.upper()}]\n{msg.text}",
                    "username": "THE BEAST",
                    "icon_emoji": ":zap:"
                }
                response = await client.post(url, json=payload)
            
            elif msg.channel.lower() == "matrix":
                # Matrix Synapse Send Message API format
                # Expects url to be: https://matrix.domain.com/_matrix/client/r0/rooms/!room:id/send/m.room.message
                payload = {
                    "msgtype": "m.text",
                    "body": msg.text,
                    "format": "org.matrix.custom.html",
                    "formatted_body": f"<strong>BEAST</strong>: {msg.text}"
                }
                response = await client.post(url, json=payload, headers=auth_header)
            
            else:
                # Fallback for others (WhatsApp/n8n hooks)
                payload = {"message": msg.text, "sender": "The Beast"}
                response = await client.post(url, json=payload)
                
            response.raise_for_status()
            
        return {"status": "success", "channel": msg.channel, "provider_status": response.status_code}
    except Exception as e:
        logger.error(f"Failed to route message to {msg.channel}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Handshake failed: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "healthy", "gateways": [k for k, v in GATEWAYS.items() if v]}
