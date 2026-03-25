import os
import requests
import json
from dotenv import load_dotenv

# 1. Load your local .env file
load_dotenv()

# 2. Grab your key (Try both common names)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("--- JARVIS Gemini API Diagnostic Tool ---")

if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in your .env file!")
    print("Please make sure your .env has: GEMINI_API_KEY=your_actual_key_here")
    exit(1)

print(f"✅ Key found: {GEMINI_API_KEY[:6]}...{GEMINI_API_KEY[-4:]}")

# 3. Prepare the request (Using Gemini 2.5 Flash Lite)
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
headers = {'Content-Type': 'application/json'}
payload = {
    "contents": [{
        "parts": [{"text": "Hello Gemini, are you alive? Please respond with 'YES' if you can hear me."}]
    }]
}

print(f"📡 Sending request to Google servers...")

try:
    # 4. Make the direct call
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    
    # 5. Analyze results
    if response.status_code == 200:
        result = response.json()
        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        print("\n✨ SUCCESS! JARVIS is thinking.")
        print(f"Gemini Response: {ai_text}")
    else:
        print(f"\n❌ API ERROR (Status {response.status_code}):")
        print(response.text)
        
        if response.status_code == 400:
            print("\n💡 Tip: This often means the API key is invalid or formatted incorrectly.")
        elif response.status_code == 403:
            print("\n💡 Tip: This means your API key doesn't have permission for Gemini Pro.")
            
except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR: Could not reach Google. Check your internet!")
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")

print("\n--- Diagnostic Complete ---")
