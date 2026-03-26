import os
import requests
import json
from google import genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables (for API Key)
load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    print("⚠️ WARNING: TELEGRAM_BOT_TOKEN is not set in environment variables.", flush=True)

MY_USER_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "0"))  
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

pending_jobs = []

# --- LLM INTEGRATION (Official SDK v1beta) ---
def call_gemini_v2(user_input):
    """Calls Gemini API via Google's official Python SDK."""
    try:
        if not GEMINI_API_KEY:
            return "Sir, I do not have an API key. Please set GEMINI_API_KEY in Render."

        # Initialize client with 2.0 Flash
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        system_instruction = (
            "You are JARVIS, an advanced AI assistant. You are currently running as a Cloud Brain on Render."
            "If the user asks for a physical action (WhatsApp, etc.), include 'COMMAND: CMD_NAME' in your response."
        )

        # Generate response
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=f"{system_instruction}\n\nUser: {user_input}"
        )
        return response.text
    except Exception as e:
        print(f"❌ API Error: {e}", flush=True)
        return f"Sir, I am experiencing a temporary core failure: {e}"

# --- TELEGRAM SENDER ---
def send_telegram_message(chat_id, text):
    """Sends a synchronous HTTP message to Telegram API."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Cannot send message: No Bot Token.", flush=True)
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        print(f"📤 Sent reply to Telegram successfully.", flush=True)
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}", flush=True)

# --- FLASK SERVER ---
app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    return "Jarvis v2.0 Beta: Neural Core Active.", 200

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handles Telegram Webhooks robustly within the main thread."""
    global pending_jobs
    
    try:
        update_data = request.get_json(force=True)
        
        # We only process message updates
        if "message" in update_data and "text" in update_data["message"]:
            msg = update_data["message"]
            chat_id = msg.get("chat", {}).get("id")
            user_text = msg.get("text", "")
            
            print(f"📨 Incoming: {user_text}", flush=True)
            
            # 1. Talk to Gemini (Synchronous SDK call)
            ai_response = call_gemini_v2(user_text)

            # 2. Process Commands
            if "COMMAND:" in ai_response:
                parts = ai_response.split("COMMAND:")
                reply = parts[0].strip() or "Acknowledged. Task sent to your local bridge."
                for part in parts[1:]:
                    cmd = part.strip()
                    if cmd:
                        pending_jobs.append(cmd)
                        print(f"⚙️ Queued Command: {cmd}", flush=True)
                send_telegram_message(chat_id, reply)
            else:
                send_telegram_message(chat_id, ai_response)
                
        return "OK", 200
    except Exception as e:
        print(f"❌ Global Webhook Error: {e}", flush=True)
        return "OK", 200 # Always return 200 to prevent Render 503

@app.route('/get_jobs', methods=['GET'])
def get_jobs():
    global pending_jobs
    jobs = list(pending_jobs)
    pending_jobs.clear()
    return jsonify(jobs)

if __name__ == "__main__":
    # If run locally with `python render_jarvis.py`, start Flask manually
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
