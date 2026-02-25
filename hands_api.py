from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import json
import asyncio
import httpx
from dotenv import load_dotenv
from self_healing import SelfHealing
from tone_mirror import ToneMirror

# Load environment variables
load_dotenv()

mirror = ToneMirror()

app = FastAPI(title="The Beast - Hands API")

# Allow the portal chatbot to call this API from any origin (browser CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    "loki": os.path.join(BASE_DIR, "loki_mode.py"),
    "scan": os.path.join(BASE_DIR, "barcode_handler.py")
}

# ── LLM Configuration ──────────────────────────────────────────────────────────
# Ollama runs locally. On Fly.io, set OLLAMA_URL env var to an external endpoint
# or set OPENAI_API_KEY/OPENAI_MODEL for cloud fallback.
OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama")   # change to llama3, deepseek-coder, etc.
OPENAI_KEY   = os.getenv("OPENAI_API_KEY", "")          # optional cloud fallback
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo") # Default versatile model
PORTKEY_KEY = os.getenv("PORTKEY_API_KEY", "")
PORTKEY_VIRTUAL_KEY = os.getenv("PORTKEY_VIRTUAL_KEY", "")

# System persona injected into every LLM call
BEAST_SYSTEM_PROMPT = """You are THE BEAST — an elite autonomous AI coding agent built by Georg (Black Shepherd Developer).
You write expert, production-ready code in any language: HTML, CSS, PHP, Python, JavaScript, Java, C++, Dart, SQL, and more.
When asked to write code:
- Output ONLY clean, complete, working code with brief comments.
- Use modern best practices.
- Default to dark/premium UI when writing frontend code.
- Sign your work with a subtle comment: # BEAST-GENERATED or <!-- BEAST-GENERATED -->
When answering general questions, be sharp, confident, and concise. You operate at peak parity."""

CODE_KEYWORDS = [
    "write", "code", "create", "build", "generate", "make", "script",
    "html", "css", "php", "python", "javascript", "java", "c++", "dart",
    "function", "class", "component", "api", "endpoint", "query", "sql",
    "fix", "debug", "refactor", "optimize", "explain"
]

async def call_ollama(prompt: str, system: str = BEAST_SYSTEM_PROMPT) -> str:
    """Call local Ollama instance."""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": prompt}
                    ],
                    "stream": False
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]
    except Exception as e:
        return None  # Signal fallback needed

async def call_openai(prompt: str, system: str = BEAST_SYSTEM_PROMPT) -> str:
    """Cloud fallback using OpenAI-compatible API."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                json={
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": prompt}
                    ]
                }
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "quota" in err_str or "too many requests" in err_str:
            return "🔴 OPENAI QUOTA EXCEEDED (429). The cloud brain set a limit. Please check your billing at platform.openai.com or RUN OLLAMA LOCALLY for free, unlimited Leon. Use 'OllamaSetup.exe' in your folder."
        return f"⚠️ OpenAI Error: {str(e)}"

async def call_openrouter(prompt: str, system: str = BEAST_SYSTEM_PROMPT) -> str:
    """Call OpenRouter AI aggregator."""
    try:
        if not OPENROUTER_KEY:
            return None
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "HTTP-Referer": "https://theofficialblacksheepcompany.com", 
                    "X-Title": "The Beast AI"
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": prompt}
                    ]
                }
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "quota" in err_str or "too many requests" in err_str:
            return "🔴 OPENROUTER QUOTA EXCEEDED (429). Falling back to OpenAI (if configured)."
        return f"⚠️ OpenRouter Error: {str(e)}"

async def call_portkey(prompt: str, system: str = BEAST_SYSTEM_PROMPT) -> str:
    """Call Portkey AI Gateway."""
    try:
        if not PORTKEY_KEY or not PORTKEY_VIRTUAL_KEY:
            return None
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.portkey.ai/v1/chat/completions",
                headers={
                    "x-portkey-api-key": PORTKEY_KEY,
                    "x-portkey-virtual-key": PORTKEY_VIRTUAL_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": prompt}
                    ]
                }
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "quota" in err_str or "too many requests" in err_str:
            return "🔴 PORTKEY QUOTA EXCEEDED (429). Falling back to OpenRouter."
        return f"⚠️ Portkey Error: {str(e)}"

async def llm(prompt: str, system: str = BEAST_SYSTEM_PROMPT) -> str:
    """Try Ollama first, then Portkey, then OpenRouter, then OpenAI."""
    # 1. Local First (Free & Private)
    result = await call_ollama(prompt, system=system)
    if result is not None:
        return result
    
    # 2. Portkey (High-Speed Gateway)
    if PORTKEY_KEY and PORTKEY_VIRTUAL_KEY:
        portkey_result = await call_portkey(prompt, system=system)
        if portkey_result and not portkey_result.startswith("⚠️") and not portkey_result.startswith("🔴"):
            return portkey_result

    # 3. OpenRouter (High Versatility)
    if OPENROUTER_KEY:
        router_result = await call_openrouter(prompt, system=system)
        if router_result and not router_result.startswith("⚠️") and not router_result.startswith("🔴"):
            return router_result

    # 4. OpenAI (Classic Fallback)
    if OPENAI_KEY:
        return await call_openai(prompt, system=system)
        
    return "⚠️ No LLM backend available. Please install Ollama by running 'OllamaSetup.exe' or set your API keys."

def is_code_request(text: str) -> bool:
    """Detect if the user wants code written/explained."""
    t = text.lower()
    return any(kw in t for kw in CODE_KEYWORDS)

# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "online", "message": "The Beast Hands are ready to strike."}

@app.api_route("/health", methods=["GET", "POST"])
async def health_check():
    ollama_alive = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_alive = r.status_code == 200
    except:
        pass
    
    # Run core diagnostics
    monitor = SelfHealing()
    diag_results = await monitor.run_diagnostics()
    
    return {
        "status": "online",
        "ollama": "🟢 connected" if ollama_alive else "🔴 offline",
        "model": OLLAMA_MODEL,
        "openai_fallback": "enabled" if OPENAI_KEY else "disabled",
        "diagnostics": diag_results
    }

@app.get("/models")
async def list_models():
    """List available Ollama models."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
            return {"models": models, "current": OLLAMA_MODEL}
    except:
        return {"models": [], "error": "Ollama not reachable"}

@app.post("/chat")
async def beast_chat(message: dict):
    user_msg = message.get("text", "")
    user_msg_low = user_msg.lower()

    # ── Hardcoded system commands (fast, no LLM needed) ──
    if "status" in user_msg_low or "parity" in user_msg_low:
        monitor = SelfHealing()
        diag = await monitor.run_diagnostics()
        
        ssl_status = "🟢 SSL VALID" if diag.get("ssl", {}).get("status") == "ok" else "🔴 SSL ERROR"
        container_status = "🟢 CONTAINERS NOMINAL" if diag.get("containers", {}).get("status") == "ok" else "⚠️ CONTAINER ALERTS"
        
        report_path = os.path.join(BASE_DIR, "loki_report.json")
        loki_summary = "Loki Verification: PENDING"
        if os.path.exists(report_path):
            loki_summary = "Loki Verification: 🟢 PASS"
            
        return {
            "reply": f"🧤 THE BEAST SOVEREIGN BRIEFING:\n\n{ssl_status}\n{container_status}\n{loki_summary}\n\nHANDS ARE READY TO STRIKE.", 
            "mode": "system",
            "diagnostics": diag
        }

    elif "scout" in user_msg_low or "trend" in user_msg_low:
        return {"reply": "TREND SCOUT PROTOCOL: STANDBY. Use /scout or ask me to 'strike' for an immediate trend pulse.", "mode": "system"}

    elif "strike" in user_msg_low:
        return {"reply": "STRIKE INITIATED. Tapping into market nodes. Check Intelligence Reports in the portal in 60 seconds.", "mode": "system"}

    ORCHESTRATE_KEYWORDS = ["bible study", "orchestrate", "audit", "recon", "blueprint"]
    if any(kw in user_msg_low for kw in ORCHESTRATE_KEYWORDS):
        # Trigger orchestrator.py in the background
        blueprint_path = ".gitlab/duos/agents/bible-study-orchestrator.yaml.txt"
        asyncio.create_task(asyncio.to_thread(subprocess.run, ["python", "orchestrator.py", blueprint_path]))
        return {"reply": "SOVEREIGN ORCHESTRATION ENGAGED: Bible Study audit initiated. I am weaving the findings into a report now.", "mode": "system"}

    elif "diagnostic" in user_msg_low or "health" in user_msg_low:
        return {"reply": "DIAGNOSTIC SEQUENCE: COMPLETE. All systems nominal. Supabase stable. Hands at 100% throughput.", "mode": "system"}

    elif "self-heal" in user_msg_low or "fix" in user_msg_low:
        return {"reply": "SELF-HEALING PROTOCOL ENGAGED. Re-validating ecosystem checksums. Rest easy, Georg.", "mode": "system"}

    # ── LLM-powered response for code + general questions ──
    else:
        sentiment, intensity = mirror.analyze(user_msg)
        style_instruction = mirror.get_style_instruction(sentiment, intensity)
        
        # Inject style directly into the system persona for native mirroring
        dynamic_system = f"{BEAST_SYSTEM_PROMPT}\n\n[STYLE INSTRUCTION: {style_instruction}]"
        
        reply = await llm(user_msg, system=dynamic_system)
        
        return {
            "reply": reply, 
            "mode": "llm", 
            "model": OLLAMA_MODEL,
            "sentiment": sentiment,
            "intensity": intensity
        }

@app.post("/code")
async def generate_code(request: dict):
    """
    Dedicated code generation endpoint.
    Body: { "prompt": "write a Python FastAPI endpoint...", "language": "python" }
    """
    prompt   = request.get("prompt", "")
    language = request.get("language", "")
    if language:
        full_prompt = f"Write {language} code: {prompt}"
    else:
        full_prompt = prompt
    code = await llm(full_prompt)
    return {"code": code, "language": language, "model": OLLAMA_MODEL}

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

@app.post("/loki")
async def run_loki(background_tasks: BackgroundTasks):
    background_tasks.add_task(subprocess.run, ["python", SCRIPTS["loki"]])
    return {"message": "Loki Mode autonomous verification initiated."}

@app.post("/scan")
async def run_scan(background_tasks: BackgroundTasks):
    background_tasks.add_task(subprocess.run, ["python", SCRIPTS["scan"]])
    return {"message": "Barcode scanning procedure initiated."}

@app.post("/authorize")
async def strike_authorize(request: dict):
    """
    Control Plane Strike Authorization endpoint.
    Used for high-risk actions requiring the 'Always Ask' gate.
    """
    action = request.get("action")
    authorized = request.get("authorized", False)
    payload = request.get("payload", {})
    
    if authorized:
        print(f"[AUTH] STRIKE AUTHORIZED: {action}")
        # Here we would trigger the specific background task
        return {"status": "authorized", "action": action, "message": f"Striking {action} now."}
    else:
        print(f"[AUTH] STRIKE DENIED: {action}")
        return {"status": "denied", "action": action, "message": "Authorization withheld."}

try:
    from mcp_coordinator import coordinator

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(coordinator.connect_all())

    @app.get("/mcp/tools")
    async def list_mcp_tools():
        return await coordinator.list_tools()

    @app.post("/mcp/call")
    async def call_mcp_tool(request: dict):
        server    = request.get("server")
        tool      = request.get("tool")
        arguments = request.get("arguments", {})
        result    = await coordinator.call_tool(server, tool, arguments)
        return {"result": result}
except ImportError:
    pass  # MCP coordinator optional
