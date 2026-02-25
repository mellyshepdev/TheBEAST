import httpx
import sys

def check_ollama():
    url = "http://localhost:11434/api/tags"
    print("Checking Ollama status...")
    try:
        resp = httpx.get(url, timeout=5.0)
        if resp.status_code == 200:
            print("[PASS] Ollama is RUNNING.")
            models = [m['name'] for m in resp.json().get('models', [])]
            if models:
                print(f"Models available: {', '.join(models)}")
            else:
                print("[WARN] No models found. Run 'ollama pull codellama' or 'ollama pull llama3'.")
        else:
            print(f"[FAIL] Ollama returned unexpected status: {resp.status_code}")
    except Exception as e:
        print(f"[FAIL] Ollama is NOT REACHABLE.")
        print("Please ensure Ollama is installed and running.")
        print("Download from https://ollama.com or run 'OllamaSetup.exe' if available.")

if __name__ == "__main__":
    check_ollama()
