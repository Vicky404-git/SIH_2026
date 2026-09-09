import subprocess
import sys
import os

def check_installed(command, name, install_url):
    """Checks if a system dependency exists."""
    try:
        # Use shell=True for Windows compatibility with certain commands
        is_windows = os.name == 'nt'
        subprocess.run([command, "--version"], capture_output=True, check=True, shell=is_windows)
        print(f"✅ {name} is installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {name} is NOT installed.")
        print(f"   Please install it manually: {install_url}")
        return False

def main():
    print("🚀 Bootstrapping DEV-das Sovereign AI Workbench...\n")

    # 1. Check system-level dependencies
    all_good = True
    all_good &= check_installed("ollama", "Ollama", "https://ollama.com/download")
    all_good &= check_installed("pandoc", "Pandoc", "https://pandoc.org/installing.html")

    if not all_good:
        print("\n⚠️ Please install the missing system dependencies above and run this script again.")
        sys.exit(1)

    # 2. Pull required models automatically
    models = ["llama3.2:3b", "qwen2.5-coder:1.5b", "qwen3-vl:4b"]
    print("\n📥 Verifying local LLMs (will download if missing)...")
    for model in models:
        print(f"   Checking/Pulling {model}...")
        # Ignore errors here so a single network blip doesn't crash the whole script
        subprocess.run(["ollama", "pull", model], shell=(os.name == 'nt'))

    # 3. Setup Python dependencies via uv
    print("\n📦 Syncing Python environment using uv...")
    try:
        subprocess.run(["uv", "sync", "--all-extras"], check=True, shell=(os.name == 'nt'))
    except FileNotFoundError:
        print("❌ 'uv' package manager is missing. Install it via: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    # 4. Launch Streamlit
    print("\n✨ Starting the Streamlit Workbench...")
    try:
        subprocess.run(["uv", "run", "streamlit", "run", "app.py"], shell=(os.name == 'nt'))
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")

if __name__ == "__main__":
    main()
