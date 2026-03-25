import os
import sys
import torch
import requests
import time

def check_voice_system():
    print("--- JARVIS Voice Diagnostic Tool ---")
    
    # 1. Check Sample File
    sample_path = "c:/Users/anger/Desktop/JARVIS_Project/anime-voice-erin-touch-2.wav"
    if os.path.exists(sample_path):
        print(f"[OK] Voice sample found: {sample_path}")
    else:
        print(f"[ERROR] Voice sample NOT found: {sample_path}")

    # 2. Check XTTS Server
    cloner_url = "http://127.0.0.1:8768/synthesize"
    try:
        print("Checking XTTS Server connection...")
        # Simple test request
        response = requests.post(cloner_url, json={"text": "Test", "language": "en"}, timeout=5)
        if response.status_code == 200:
            print("[OK] XTTS Server is running and responding.")
        else:
            print(f"[ERROR] XTTS Server returned error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] XTTS Server is NOT running on port 8768.")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

    # 3. Check GPU/Torch
    print(f"Checking Torch/CUDA...")
    print(f"Torch Version: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"[OK] CUDA is available. GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("[WARNING] CUDA NOT available. XTTS will be extremely slow on CPU, which might cause timeouts.")

    # 4. Check dependencies
    try:
        import TTS
        print(f"[OK] Coqui TTS library is installed.")
    except ImportError:
        print("[ERROR] Coqui TTS library is NOT installed. Run: pip install TTS")

if __name__ == "__main__":
    check_voice_system()
