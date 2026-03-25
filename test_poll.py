import time
import requests
from agents.messaging_agent import MessagingAgent

# Initialize your WhatsApp agent
agent = MessagingAgent()
RENDER_URL = "https://jarvis-cloud-brain.onrender.com/get_jobs"

print(f"🚀 JARVIS Local Polling Engine Started!")
print(f"📡 Monitoring: {RENDER_URL}")
print("Waiting for jobs from Cloud...")

while True:
    try:
        # 1. Safely poll the Render Cloud
        response = requests.get(RENDER_URL, timeout=12)
        
        if response.status_code == 200:
            jobs = response.json()
            
            if jobs and len(jobs) > 0:
                print(f"\n✅ Found {len(jobs)} pending task(s)! Processing...")
                
                for job in jobs:
                    # Robust handling for both raw strings and dictionaries
                    if isinstance(job, dict):
                        task_text = job.get("text", "Unknown Job")
                    else:
                        task_text = str(job)
                    
                    print(f"👉 Executing: {task_text}")
                    
                    # Pass the command to our local execution agent
                    agent.execute_task(task_text)
            else:
                # Keep-alive visual feedback
                print(".", end="", flush=True)
        else:
            print(f"\n⚠️ Cloud returned status: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Loop Error: {e}")
    
    # Poll every 12 seconds as requested
    time.sleep(12)