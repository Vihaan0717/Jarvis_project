import os
import requests
import json
from dotenv import load_dotenv

# Load your local .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("--- JARVIS Model Discovery Tool ---")

if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in your .env file!")
    exit(1)

# Endpoint to list models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"

try:
    print("📡 Querying Google for available models...")
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! Here are your available models:")
        for model in data.get('models', []):
            name = model.get('name')
            methods = model.get('supportedGenerationMethods', [])
            if 'generateContent' in methods:
                print(f"- {name} (Supports: generateContent)")
    else:
        print(f"\n❌ ERROR (Status {response.status_code}):")
        print(response.text)

except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")

print("\n--- Discovery Complete ---")
