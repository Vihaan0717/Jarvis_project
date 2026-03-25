import os
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_USER_ID = int(os.getenv("MY_USER_ID", "0"))

# Global references for cross-thread communication
telegram_app = None
telegram_loop = None

# --- JOB QUEUE (Memory-based) ---
pending_jobs = []

# --- FLASK SERVER (Health Check & Bridge API) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Jarvis Online", 200

@app.route('/get_jobs', methods=['GET'])
def get_jobs():
    """Returns the list of pending tasks and immediately clears them."""
    global pending_jobs
    
    # 1. Grab current tasks
    jobs_to_send = list(pending_jobs)
    
    # 2. CLEAR the queue immediately
    pending_jobs.clear()
    
    # Use jsonify for proper JSON response formatting
    return jsonify(jobs_to_send)

@app.route('/complete_job', methods=['POST'])
def complete_job():
    """Notifies results via Telegram."""
    result_data = request.json.get('result', 'Success!')
    
    # --- NOTIFY USER VIA TELEGRAM ---
    if telegram_app and telegram_loop:
        msg = f"✅ Task Completed.\nResult: {result_data}"
        asyncio.run_coroutine_threadsafe(
            telegram_app.bot.send_message(chat_id=MY_USER_ID, text=msg),
            telegram_loop
        )
    return jsonify({"status": "success"})

# --- TELEGRAM BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the authorized user."""
    if update.effective_user.id != MY_USER_ID:
        return
    await update.message.reply_text("Cloud Brain Online. Simple command queue active.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Queues the raw user command."""
    if update.effective_user.id != MY_USER_ID:
        return
    
    user_text = update.message.text
    global pending_jobs
    pending_jobs.append(user_text)
    
    print(f"📥 Queued command: {user_text}")
    await update.message.reply_text(f"Command Queued: {user_text}")

def run_flask():
    """Starts the Flask server."""
    # Note: Render provides PORT env var
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def main_bot():
    """Main entry point for the Telegram bot."""
    global telegram_app, telegram_loop
    if not TELEGRAM_TOKEN or not MY_USER_ID:
        print("Error: TELEGRAM_TOKEN or MY_USER_ID missing!")
        return

    telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    telegram_loop = asyncio.get_running_loop()
    
    # Handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Starting Telegram Bot polling...")
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    
    # Keep alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # Start Flask in a background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run Telegram Bot in the main loop
    asyncio.run(main_bot())
