import os
import asyncio
import threading
from flask import Flask, request
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
job_queue = []

# --- FLASK SERVER (Health Check & Bridge API) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Jarvis Online", 200

@app.route('/get_jobs', methods=['GET'])
def get_jobs():
    """Returns the next pending job based on target (laptop/mobile)."""
    target = request.args.get('target', 'laptop')
    if job_queue:
        for job in job_queue:
            if job['status'] == 'pending' and job.get('target', 'laptop') == target:
                return {"job": job}, 200
    return {"job": None}, 200

@app.route('/complete_job', methods=['POST'])
def complete_job():
    """Marks a job as completed and notifies results via Telegram."""
    job_id = request.json.get('job_id')
    result_data = request.json.get('result', 'Success!')
    
    for job in job_queue:
        if job['id'] == job_id:
            job['status'] = 'completed'
            job['result'] = result_data
            
            # --- NOTIFY USER VIA TELEGRAM ---
            if telegram_app and telegram_loop:
                target_name = job.get('target', 'laptop').capitalize()
                msg = f"✅ Job #{job_id} ({job['type']}) completed on {target_name}.\nResult: {result_data}"
                asyncio.run_coroutine_threadsafe(
                    telegram_app.bot.send_message(chat_id=MY_USER_ID, text=msg),
                    telegram_loop
                )
            
            return {"status": "success"}, 200
            
    return {"status": "not_found"}, 404

# --- TELEGRAM BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the authorized user."""
    if update.effective_user.id != MY_USER_ID:
        return
    await update.message.reply_text("Cloud Brain Online. Ecosystem expansion complete. Monitoring Laptop & Mobile targets.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echoes messages or queues jobs for the authorized user."""
    if update.effective_user.id != MY_USER_ID:
        return
    
    user_text = update.message.text.lower()
    
    # --- LAPTOP: WhatsApp Send ---
    if user_text.startswith("send whatsapp to"):
        try:
            parts = user_text.split(":", 1)
            header = parts[0].replace("send whatsapp to", "").strip()
            message = parts[1].strip()
            
            job_id = str(len(job_queue) + 1)
            job_queue.append({
                "id": job_id, "type": "whatsapp_send", "target": "laptop",
                "contact": header, "message": message, "status": "pending"
            })
            await update.message.reply_text(f"Laptop Job Queued (#{job_id}): Sending WhatsApp to {header}.")
            return
        except:
            await update.message.reply_text("Error. Use: 'send whatsapp to Name: Message'")
            return

    # --- MOBILE: Termux API Actions ---
    elif user_text.startswith("mobile"):
        command_map = {
            "battery": "battery",
            "torch on": "torch_on",
            "torch off": "torch_off",
            "location": "location"
        }
        
        found_cmd = None
        for key, val in command_map.items():
            if key in user_text:
                found_cmd = val
                break
        
        if found_cmd:
            job_id = str(len(job_queue) + 1)
            job_queue.append({
                "id": job_id, "type": f"mobile_{found_cmd}", "target": "mobile",
                "status": "pending"
            })
            await update.message.reply_text(f"Mobile Job Queued (#{job_id}): Triggering {found_cmd}...")
            return
        else:
            await update.message.reply_text("Unknown Mobile Command. Available: battery, torch on, torch off, location.")
            return

    response = f"Cloud Brain received: {user_text}"
    await update.message.reply_text(response)

def run_flask():
    """Starts the Flask server."""
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
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    asyncio.run(main_bot())
