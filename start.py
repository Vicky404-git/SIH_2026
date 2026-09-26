import subprocess
import sys
import os
import time
import webbrowser

def check_installed(command, name, install_url):
    """Checks if a system dependency exists."""
    try:
        is_windows = os.name == 'nt'
        subprocess.run([command, "--version"], capture_output=True, check=True, shell=is_windows)
        print(f"✅ {name} is installed and available.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"⚠️ {name} is not found on PATH ({install_url}).")
        return False

def check_local_models():
    """Detects locally available Ollama models without blocking or downloading."""
    try:
        import ollama
        resp = ollama.list()
        models = getattr(resp, "models", None)
        if models is None and isinstance(resp, dict):
            models = resp.get("models", [])
        models = models or []

        names = []
        for m in models:
            n = getattr(m, "model", None) or (m.get("model") or m.get("name") if isinstance(m, dict) else str(m))
            if n:
                names.append(n)

        if names:
            print(f"✅ Local Ollama model(s) detected: {', '.join(names)}")
            return names
        else:
            print("⚠️ No local Ollama models found. You can pull one using: ollama pull qwen3-vl:4b")
            return []
    except Exception as e:
        print(f"⚠️ Could not query Ollama service: {e}")
        return []

def main():
    print("=" * 65)
    print("🔒 SOVEREIGN AI — ON-PREMISE AGENTIC WORKBENCH (FULL-STACK)")
    print("   SIH PS 26117 · Air-Gapped Industrial Intelligence")
    print("=" * 65 + "\n")

    # 1. Dependency checks
    check_installed("ollama", "Ollama", "https://ollama.com/download")
    check_installed("pandoc", "Pandoc", "https://pandoc.org/installing.html")

    # 2. Check local model availability
    print("\n🔍 Verifying AI runtime...")
    check_local_models()

    # 3. Launch Unified FastAPI Server (Backend + Frontend)
    print("\n🚀 Starting Sovereign AI Unified Server...")
    print("   🌐 Web Application: http://127.0.0.1:8000/")
    print("   📖 OpenAPI Docs:     http://127.0.0.1:8000/docs")
    print("   👤 Default Logins:   admin / admin123  (or engineer / eng123)")
    print("\n[INFO] Press Ctrl+C in this terminal to shut down.\n")

    def open_browser():
        time.sleep(1.2)
        webbrowser.open("http://127.0.0.1:8000/")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        cmd = [sys.executable, "-m", "uvicorn", "api_server:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Sovereign AI server gracefully...")

if __name__ == "__main__":
    main()
