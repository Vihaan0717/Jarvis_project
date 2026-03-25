import os
import asyncio
import threading
import requests
import json
from google import genai
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables (for API Key)
load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    print("⚠️ WARNING: TELEGRAM_BOT_TOKEN is not set in environment variables.")
MY_USER_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "0"))  # Still useful but can be hardcoded if needed
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Global references
telegram_app = None
telegram_loop = None
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
        print(f"❌ API Error: {e}")
        return f"Sir, I am experiencing a temporary core failure: {e}"

# --- FLASK SERVER ---
app = Flask(__name__)

# Track if thread is started to prevent duplicates per worker
bot_thread_started = False

@app.route('/', methods=['GET', 'POST'])
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handles Telegram Webhooks with a global safety net."""
    global bot_thread_started
    
    # Lazy Initialization: This guarantees the thread starts INSIDE the worker process
    # after Gunicorn has finished forking, avoiding the os.fork() thread-killing issue.
    if not bot_thread_started:
        threading.Thread(target=start_bot_thread, daemon=True).start()
        bot_thread_started = True

    try:
        if request.method == 'GET':
            return "Jarvis v2.0 Beta: Neural Core Active.", 200
        
        # Process POST (Telegram Update)
        update_data = request.get_json(force=True)
        if telegram_app and telegram_loop:
            # Spawn background thread to process so we can return 200 OK instantly
            threading.Thread(target=process_background_update, args=(update_data,), daemon=True).start()
        else:
            print("⚠️ WARNING: Telegram Bot is still initializing in the background. Please try again in a few seconds.")
            
        return "OK", 200
    except Exception as e:
        print(f"❌ Global Webhook Error: {e}")
        return "OK", 200 # Always return 200 to prevent Render 503

def process_background_update(update_data):
    """Worker thread for Telegram updates."""
    global telegram_app, telegram_loop
    try:
        update = Update.de_json(update_data, telegram_app.bot)
        future = asyncio.run_coroutine_threadsafe(
            telegram_app.process_update(update),
            telegram_loop
        )
        future.result(timeout=60)
    except Exception as e:
        print(f"❌ Background Process Error: {e}")

@app.route('/get_jobs', methods=['GET'])
def get_jobs():
    global pending_jobs
    jobs = list(pending_jobs)
    pending_jobs.clear()
    return jsonify(jobs)

# --- TELEGRAM BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Neural core v2.0 online, Sir. Your requests are prioritized.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes incoming Telegram messages with a localized safety net."""
    try:
        user_text = update.message.text
        print(f"📨 Incoming: {user_text}")

        # 1. Talk to Gemini (SDK)
        ai_response = await asyncio.to_thread(call_gemini_v2, user_text)

        # 2. Process Commands
        if "COMMAND:" in ai_response:
            global pending_jobs
            parts = ai_response.split("COMMAND:")
            reply = parts[0].strip() or "Acknowledged. Task sent to your local bridge."
            for part in parts[1:]:
                pending_jobs.append(part.strip())
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text(ai_response)

    except Exception as e:
        print(f"❌ Message Handler Error: {e}")
        # We don't return OK here, we just finish the async coroutine
        # The webhook caller already got their OK, 200.

async def main_bot(loop):
    global telegram_app, telegram_loop
    telegram_loop = loop
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ CRITICAL: TELEGRAM_BOT_TOKEN is missing. Bot background loop cannot start.")
        return

    telegram_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 JARVIS Webhook Bridge Initializing...")
    await telegram_app.initialize()
    await telegram_app.start()
    
    while True:
        await asyncio.sleep(3600)

def start_bot_thread():
    """Starts the Telegram bot inside a dedicated asyncio event loop thread."""
    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    bot_loop.run_until_complete(main_bot(bot_loop))

# Start the background bot thread globally so it runs even under Gunicorn
threading.Thread(target=start_bot_thread, daemon=True).start()

if __name__ == "__main__":
    # If run locally with `python render_jarvis.py`, start Flask manually
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
