import time
import requests
import threading
import asyncio
import os
from agents.messaging_agent import MessagingAgent
from core.logger import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger("CloudBridge")

# --- CONFIGURATION ---
RENDER_URL = "https://jarvis-cloud-brain.onrender.com"

class CloudBridge:
    """
    Background polling mechanism to fetch jobs from Render Cloud 
    and execute them locally using Playwright and WhatsApp tools.
    """
    def __init__(self):
        self.messaging = MessagingAgent()
        self.is_running = False
        self.thread = None

    def start(self):
        """Starts the bridge in a background thread as requested."""
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info(f"Cloud Bridge started in background thread. Polling {RENDER_URL}/get_jobs")

    def stop(self):
        """Stops the background polling."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Cloud Bridge terminated.")

    def _loop(self):
        """Main polling loop (runs every 10-15 seconds)."""
        while self.is_running:
            try:
                # 1. Pull from Render (Using specifically requested endpoint)
                response = requests.get(f"{RENDER_URL}/get_jobs", timeout=12)
                
                if response.status_code == 200:
                    job_data = response.json().get("job")
                    
                    if job_data and job_data["status"] == "pending":
                        job_id = job_data.get("id")
                        job_type = job_data.get("type")
                        
                        logger.info(f"🔄 Processing Cloud Job #{job_id} ({job_type})")
                        
                        if job_type == "whatsapp_send":
                            contact = job_data.get("contact")
                            message = job_data.get("message")
                            
                            # 2. Execute Playwright via local WhatsApp automation
                            success = asyncio.run(self.messaging.send_message(contact, message))
                            
                            if success:
                                # 3. Update Render (Using specifically requested POST confirmation)
                                logger.info(f"✅ Executed locally. Notifying Cloud: Job Completed!")
                                requests.post(
                                    f"{RENDER_URL}/complete_job", 
                                    json={"job_id": job_id, "status": "Job Completed!"},
                                    timeout=10
                                )
                
            except Exception as e:
                logger.error(f"Cloud Bridge Polling Error: {e}")
            
            # Polling delay (10-15 seconds as requested)
            time.sleep(12)

if __name__ == "__main__":
    # For manual testing
    bridge = CloudBridge()
    bridge.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        bridge.stop()
