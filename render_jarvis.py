import os
import asyncio
import threading
import requests
import json
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
MY_USER_ID = int(os.getenv("MY_USER_ID", os.getenv("AUTHORIZED_CHAT_ID", "0")))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Global references for cross-thread communication
telegram_app = None
telegram_loop = None

# --- JOB QUEUE (Memory-based) ---
pending_jobs = []

# --- LLM INTEGRATION (Gemini Pro) ---
def call_gemini_llm(user_input):
    """Calls Gemini API via requests (simulating a cloud brain)."""
    if not GEMINI_API_KEY:
        return "Sir, my Gemini API key is missing. Please check your Render environment variables."
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # System prompt to guide JARVIS and command routing
    system_instruction = (
        "You are JARVIS, an advanced AI assistant. You are currently running as a Cloud Brain on Render."
        "If the user asks for a physical action like sending a WhatsApp or opening an app, you must "
        "include the command in your response prefixed by 'COMMAND:'. For example: 'COMMAND: SEND_WHATSAPP to Mom: Hello'."
        "Otherwise, respond conversationally."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_instruction}\n\nUser: {user_input}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        result = response.json()
        if 'candidates' in result:
            ai_text = result['candidates'][0]['content']['parts'][0]['text']
            return ai_text
        else:
            return f"Error from AI Core: {json.dumps(result)}"
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Sir, I am experiencing a temporary disconnection from my neural core."

# --- FLASK SERVER (Health Check & Bridge API) ---
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handles Telegram Webhooks by spawning a background thread to prevent timeouts."""
    if request.method == 'GET':
        return "Jarvis Cloud Brain: Online & Ready", 200
    
    # Process POST (Telegram Update)
    if telegram_app and telegram_loop:
        try:
            update_data = request.get_json(force=True)
            
            # CRITICAL: Spawn a background thread for ALL processing
            # This allows Flask to return 200 OK instantly to Telegram/Render
            threading.Thread(target=process_background_update, args=(update_data,), daemon=True).start()
            
            return "OK", 200 # Immediate success response
        except Exception as e:
            print(f"⚠️ Webhook Error: {e}")
            return "OK", 200 # Return 200 anyway to stop Telegram retries
            
    return "Bot Not Initialized", 503

def process_background_update(update_data):
    """Background thread worker to process the Telegram update without blocking Flask."""
    global telegram_app, telegram_loop
    try:
        # Convert raw JSON to Update object
        update = Update.de_json(update_data, telegram_app.bot)
        
        # Schedule the update processing on the bot's event loop
        # and wait for it to complete or timeout (independent of the Flask request)
        future = asyncio.run_coroutine_threadsafe(
            telegram_app.process_update(update),
            telegram_loop
        )
        # We wait up to 60s for the background "thinking" to finish
        future.result(timeout=60) 
    except Exception as e:
        print(f"❌ Background Process Error: {e}")

@app.route('/get_jobs', methods=['GET'])
def get_jobs():
    """Returns the list of pending tasks and immediately clears them."""
    global pending_jobs
    jobs_to_send = list(pending_jobs)
    pending_jobs.clear()
    return jsonify(jobs_to_send)

@app.route('/complete_job', methods=['POST'])
def complete_job():
    """Notifies results via Telegram."""
    data = request.json
    result_data = data.get('result', 'Task marked as complete.')
    
    if telegram_app and telegram_loop:
        msg = f"✅ JARVIS (Local): {result_data}"
        asyncio.run_coroutine_threadsafe(
            telegram_app.bot.send_message(chat_id=MY_USER_ID, text=msg),
            telegram_loop
        )
    return jsonify({"status": "success"})

# --- TELEGRAM BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the authorized user."""
    if update.effective_user.id != MY_USER_ID: return
    await update.message.reply_text("Cloud Brain v2.2 Online. Background threading active. Any request is now immediately acknowledged, Sir.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes message via LLM, replies immediately, and queues commands if needed."""
    if update.effective_user.id != MY_USER_ID: return
    
    user_text = update.message.text
    print(f"📨 From Boss: {user_text}")

    # 1. Get AI Response (Thinking in the cloud)
    # We wrap this in a localized try/except to prevent thread crashes
    try:
        ai_response = await asyncio.to_thread(call_gemini_llm, user_text)
    except Exception as e:
        logger_err = f"AI Core Exception: {e}"
        print(logger_err)
        await update.message.reply_text("Sir, I encountered an internal error in my neural core. Please check my logs.")
        return

    # 2. Check for hardware commands (Smart Routing)
    if "COMMAND:" in ai_response:
        global pending_jobs
        parts = ai_response.split("COMMAND:")
        clean_reply = parts[0].strip()
        
        for part in parts[1:]:
            cmd = part.strip()
            pending_jobs.append(cmd)
            print(f"📥 Queued hardware command: {cmd}")
        
        reply_to_send = clean_reply if clean_reply else "Recognized. I've queued that for your hardware bridge, Sir."
        await update.message.reply_text(reply_to_send)
    else:
        # 3. Standard conversational reply
        await update.message.reply_text(ai_response)

def run_flask():
    """Starts the Flask server."""
    port = int(os.environ.get("PORT", 10000))
    # Note: Use threaded=True for better concurrency if needed, 
    # but run_coroutine_threadsafe handles the sync/async bridge.
    app.run(host='0.0.0.0', port=port)

async def main_bot():
    """Main entry point for the Telegram bot."""
    global telegram_app, telegram_loop
    if not TELEGRAM_TOKEN or not MY_USER_ID:
        print("CRITICAL: TELEGRAM_TOKEN or MY_USER_ID missing!")
        return

    # Initialize the app WITHOUT polling
    telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    telegram_loop = asyncio.get_running_loop()
    
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Cloud Brain Webhook Bridge Initialized.")
    await telegram_app.initialize()
    await telegram_app.start()
    
    # We no longer call start_polling() here. 
    # Flask will feed updates to the bot via the webhook route.
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    asyncio.run(main_bot())
