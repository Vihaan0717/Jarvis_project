import time
import requests
from agents.messaging_agent import MessagingAgent

agent = MessagingAgent()
RENDER_URL = "https://jarvis-cloud-brain.onrender.com/get_jobs"

print(f"🚀 Force-polling Render at {RENDER_URL}...")

while True:
    try:
        response = requests.get(RENDER_URL, timeout=10)
        
        if response.status_code == 200:
            jobs = response.json()
            
            if jobs:
                print(f"\n✅ Found {len(jobs)} jobs! Processing...")
                for job in jobs:
                    # --- FIXED SECTION ---
                    # 1. If Render sends it as a dictionary
                    if isinstance(job, dict):
                        task_text = job.get("text", "")
                    # 2. If Render sends it as a raw string
                    else:
                        task_text = str(job)
                    # ---------------------

                    print(f"👉 Executing Task: {task_text}")
                    agent.execute_task(task_text)
            else:
                print(".", end="", flush=True)
                
    except Exception as e:
        print(f"\n❌ Loop Error: {e}")
        
    time.sleep(12)