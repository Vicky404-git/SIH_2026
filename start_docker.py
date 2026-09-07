import subprocess
import sys
import os

def check_installed(command, name):
    """Checks if a system dependency exists."""
    is_windows = os.name == 'nt'
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True, shell=is_windows)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {name} is NOT installed or not in PATH.")
        return False

def configure_ollama_network():
    """Cross-platform fix to allow Docker to talk to the host's Ollama."""
    print("\n🔧 Configuring Ollama to accept Docker network connections...")
    
    if sys.platform == "win32":
        # Windows: Set user environment variable
        subprocess.run('setx OLLAMA_HOST "0.0.0.0"', shell=True, capture_output=True)
        print("✅ Windows: OLLAMA_HOST set. (If Ollama fails to connect, manually restart the Ollama app from your system tray).")
        
    elif sys.platform == "darwin":
        # macOS: Set launchctl environment variable
        subprocess.run('launchctl setenv OLLAMA_HOST "0.0.0.0"', shell=True, capture_output=True)
        print("✅ macOS: OLLAMA_HOST set. (If Ollama fails to connect, completely quit and reopen the Ollama app).")
        
    elif sys.platform.startswith("linux"):
        # Linux: Create systemd override (requires sudo)
        print("Linux detected. You may be prompted for your sudo password to configure the Ollama service.")
        override_dir = "/etc/systemd/system/ollama.service.d"
        override_file = f"{override_dir}/override.conf"
        bash_cmd = f"""
        mkdir -p {override_dir} &&
        echo '[Service]\nEnvironment="OLLAMA_HOST=0.0.0.0:11434"' > {override_file} &&
        systemctl daemon-reload &&
        systemctl restart ollama
        """
        try:
            subprocess.run(["sudo", "sh", "-c", bash_cmd], check=True)
            print("✅ Linux: Ollama configured and restarted automatically.")
        except subprocess.CalledProcessError:
            print("❌ Failed to configure Ollama automatically. You may need to run this script with sudo.")

def main():
    print("🚀 Bootstrapping Containerized Sovereign AI Workbench...\n")

    if not check_installed("docker", "Docker"):
        print("Please install Docker Desktop: https://www.docker.com/products/docker-desktop/")
        sys.exit(1)
        
    if not check_installed("ollama", "Ollama"):
        print("Please install Ollama: https://ollama.com/download")
        sys.exit(1)

    # 1. Apply the cross-platform network fix
    configure_ollama_network()

    # 2. Automatically pull the required models
    models = ["llama3.2:3b", "qwen2.5-coder:1.5b", "qwen3-vl:4b"]
    print("\n📥 Verifying local LLMs (will download if missing)...")
    for model in models:
        print(f"   Checking/Pulling {model}...")
        subprocess.run(["ollama", "pull", model], shell=(os.name == 'nt'))

    # 3. Launch Docker Compose
    print("\n✨ Starting the Dockerized Workbench...")
    try:
        subprocess.run(["docker", "compose", "up", "--build"], shell=(os.name == 'nt'))
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")

if __name__ == "__main__":
    main()
