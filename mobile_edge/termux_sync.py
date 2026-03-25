import time
import requests
import subprocess
import json
import os

# --- CONFIGURATION ---
# Replace with your actual Render URL
RENDER_URL = os.environ.get("RENDER_URL", "https://jarvis-cloud-brain.onrender.com")

def run_termux_command(command_list):
    """Safely executes a Termux API command and returns the output."""
    try:
        output = subprocess.check_output(command_list, stderr=subprocess.STDOUT)
        return output.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8').strip()}"
    except FileNotFoundError:
        return "Error: Termux:API not installed or command not found."
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

def get_battery_status():
    result = run_termux_command(["termux-battery-status"])
    try:
        data = json.loads(result)
        return f"Battery: {data.get('percentage')}% ({data.get('status')})"
    except:
        return result

def set_torch(state):
    # state should be "on" or "off"
    return run_termux_command(["termux-torch", state])

def get_location():
    # Use -p last to get last known location quickly, or -s for network
    result = run_termux_command(["termux-location", "-p", "last"])
    try:
        data = json.loads(result)
        return f"Lat: {data.get('latitude')}, Lon: {data.get('longitude')}"
    except:
        return result

def main():
    print(f"📱 Termux Mobile Edge Active. Polling {RENDER_URL}...")
    
    while True:
        try:
            # 1. Poll Render for Mobile Jobs
            response = requests.get(f"{RENDER_URL}/get_jobs?target=mobile", timeout=10)
            
            if response.status_code == 200:
                job_data = response.json().get("job")
                
                if job_data and job_data["status"] == "pending":
                    job_id = job_data["id"]
                    job_type = job_data["type"]
                    print(f"📥 Received Job #{job_id}: {job_type}")
                    
                    result = "Unknown command"
                    
                    # 2. Execute natively in Termux
                    if job_type == "mobile_battery":
                        result = get_battery_status()
                    elif job_type == "mobile_torch_on":
                        result = set_torch("on")
                    elif job_type == "mobile_torch_off":
                        result = set_torch("off")
                    elif job_type == "mobile_location":
                        result = get_location()
                    
                    # 3. Post Back Result
                    print(f"📤 Job #{job_id} done. Result: {result}")
                    requests.post(f"{RENDER_URL}/complete_job", json={
                        "job_id": job_id,
                        "result": result
                    }, timeout=10)
            
        except requests.exceptions.RequestException as e:
            # Silent during network drops
            pass
        except Exception as e:
            print(f"Loop Error: {e}")
            
        # 4. Respectful 15s delay
        time.sleep(15)

if __name__ == "__main__":
    main()
