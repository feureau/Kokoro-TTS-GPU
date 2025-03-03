import os
import sys
import subprocess
import urllib.request
import zipfile

PYTHON_VERSION = "3.12.0"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
VENV_NAME = ".venv"

def setup_environment():
    # Check for existing Python 3.12
    if not os.path.exists(f"python-{PYTHON_VERSION}"):
        print("Downloading Python 3.12...")
        try:
            urllib.request.urlretrieve(PYTHON_URL, "python-embed.zip")
            with zipfile.ZipFile("python-embed.zip", 'r') as zip_ref:
                zip_ref.extractall(f"python-{PYTHON_VERSION}")
            os.remove("python-embed.zip")
        except Exception as e:
            print(f"Failed to download Python: {e}")
            sys.exit(1)

    # Install UV if missing
    try:
        subprocess.run(["uv", "--version"], check=True, stdout=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Installing uv...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)

    # Create virtual environment
    python_path = os.path.abspath(f"python-{PYTHON_VERSION}/python.exe")
    print(f"Creating virtual environment with Python {PYTHON_VERSION}...")
    subprocess.run(["uv", "venv", VENV_NAME, "--python", python_path], check=True)

    # Install dependencies
    print("Installing dependencies...")
    subprocess.run(["uv", "sync"], check=True)

    # Activation instructions
    print("\nSetup complete! Activate the environment with:")
    print(f"Windows Command Prompt:  {VENV_NAME}\\Scripts\\activate.bat")
    print(f"PowerShell:             .\\{VENV_NAME}\\Scripts\\Activate.ps1")
    print("\nThen run: python kokoro-tts alice.txt output.wav")

if __name__ == "__main__":
    setup_environment()