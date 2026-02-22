import httpx
import asyncio

async def test_broadcast():
    url = "https://beast-openclaw.fly.dev/broadcast"
    payload = {
        "text": "Global Broadcast Test - Leon is Online",
        "priority": "high"
    }
    print(f"Sending broadcast to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_broadcast())
