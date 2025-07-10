# ai_service/cli.py

import os
import subprocess
from pathlib import Path

def ensure_spacy_model():
    try:
        import en_core_web_md
    except ImportError:
        print("📦 Downloading missing spaCy model...")
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_md"], check=True)

def start_docker_container():
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=openchs", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "openchs" not in result.stdout:
            print("🐳 Starting Docker container with docker compose...")
            subprocess.run(["docker", "compose", "up", "-d"], check=True)
        else:
            print("✅ Docker container 'openchs' is already running.")
    except Exception as e:
        print(f"⚠️ Docker might not be running or installed: {e}")

def main():
    print("🔧 Starting OpenCHS service...")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_service.settings")

    # Step 0: Ensure spaCy model
    ensure_spacy_model()

    # Step 1: Start Docker (if applicable)
    start_docker_container()

    # Step 2: Ensure model folders exist
    models_path = Path("models")
    if not models_path.exists():
        print("📁 Creating models folder...")
        models_path.mkdir(parents=True, exist_ok=True)
        (models_path / "whisper-base").mkdir(exist_ok=True)
        (models_path / "flan-t5-small").mkdir(exist_ok=True)

    # Step 3: Run Django migrations
    print("⚙️ Running Django migrations...")
    subprocess.call(["python", "manage.py", "migrate"])

    # Step 4: Start development server
    print("🚀 S
