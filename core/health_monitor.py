import psutil
from core.logger import get_logger

# Give the Nervous System a voice using the logger we just built
logger = get_logger("NervousSystem")

class HealthMonitor:
    """Tracks JARVIS's physical hardware vitals."""
    
    @staticmethod
    def check_vitals():
        # Feel the hardware (Checks CPU and RAM)
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        
        # Check if the laptop is plugged into the wall
        battery = psutil.sensors_battery()
        battery_level = battery.percent if battery else 100
        is_plugged_in = battery.power_plugged if battery else True

        # Map the hardware stats to JARVIS's "Biological States"
        state = "Alert & Healthy"
        
        if cpu_usage > 80:
            state = "Stressed (CPU Running Hot)"
            logger.warning(f"High CPU detected: {cpu_usage}% - Pausing heavy thoughts.")
            
        if battery_level < 20 and not is_plugged_in:
            state = "Fatigued (Low Battery)"
            logger.warning(f"Low battery detected: {battery_level}% - Disabling cloud mind.")

        vitals = {
            "cpu_percent": cpu_usage,
            "ram_percent": ram_usage,
            "battery_percent": battery_level,
            "plugged_in": is_plugged_in,
            "biological_state": state
        }
        
        # Write the final checkup into the diary
        logger.info(f"Vitals Checked - State: {state} | CPU: {cpu_usage}% | RAM: {ram_usage}%")
        return vitals

# This block lets us test the file directly!
if __name__ == "__main__":
    print("🩺 Checking JARVIS's vitals...")
    HealthMonitor.check_vitals()