import sys
import time
import os
import threading
import webbrowser
import subprocess
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

from core.logger import get_logger
from core.avatar_server import avatar_server_instance
from agents.voice_agent import VoiceSpeaker
from agents.voice_agent import VoiceListener
from core.avatar_shell import launch_shell
from agents.biometric_agent import BiometricGuard
from main import boot_sequence, foreground_loop, alert_queue
from core.background_brain import BackgroundBrain
import core.orchestrator as orchestrator
from core.telegram_service import TelegramService
import asyncio

logger = get_logger("AvatarMain_Desktop")

def request_app_quit():
    """Simple helper to exit the program."""
    logger.info("Requesting system shutdown...")
    os._exit(0)

def _start_static_server(port: int = 8766):
    """Serve the project directory over HTTP."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    handler = SimpleHTTPRequestHandler
    TCPServer.allow_reuse_address = True
    with TCPServer(("127.0.0.1", port), handler) as httpd:
        logger.info(f"Static HTTP server for avatar running on http://127.0.0.1:{port}")
        httpd.serve_forever()

def jarvis_avatar_worker():
    """Worker thread that runs the backend logic."""
    logger.info("Starting JARVIS Worker Thread...")
    speaker = VoiceSpeaker()
    listener = VoiceListener()
    
    # Give the shell a moment to initialize and show the loading screen
    time.sleep(3)

    # --- START TELEGRAM SERVICE EARLY (Before Biometric Scan) ---
    telegram_service = TelegramService(orchestrator=orchestrator)
    orchestrator.telegram_service_instance = telegram_service
    
    def start_telegram_sync():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        telegram_service.loop = loop
        loop.run_until_complete(telegram_service.start())
        loop.run_forever()

    telegram_thread = threading.Thread(target=start_telegram_sync, daemon=True)
    telegram_thread.start()

    # 1. Initialize Biometric Check & Avatar Server Link
    guard = BiometricGuard(telegram_service=telegram_service)
    avatar_server_instance.biometric_guard = guard
    avatar_server_instance.toolbox = orchestrator.hands.toolbox
    
    # 2. Start Avatar Server (Tracking) IMMEDIATELY so it's responsive from the start
    try:
        logger.info("Starting Avatar Server Tracking early...")
        avatar_server_instance.start()
        time.sleep(1) # Give camera a moment to initialize
    except Exception as e:
        logger.error(f"Failed to start Avatar Server: {e}")
        request_app_quit()
        return

    # 3. Start Biometric Check (Uses shared frame from server)
    if not boot_sequence(speaker, guard=guard, telegram_service=telegram_service):
        logger.error("Boot sequence failed. Shutting down entire system.")
        request_app_quit()
        return
    
    # 4. Start Voice Cloner Server (XTTSv2)
    try:
        logger.info("Starting local Voice Cloner Server (XTTSv2)...")
        subprocess.Popen([sys.executable, "services/voice_cloner_server.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        time.sleep(8)
    except Exception as e:
        logger.error(f"Failed to start Voice Cloner Server: {e}")

    background_brain = BackgroundBrain(alert_queue)
    background_brain.start()

    # 6. RUN FOREGROUND LOOP
    try:
        if listener.is_available():
            foreground_loop(speaker, listener, background_brain, guard=guard, telegram_service=telegram_service, skip_greeting=True)
        else:
            logger.warning("Microphone backend unavailable. Entering standby mode.")
            while True:
                time.sleep(1)
    finally:
        if guard: guard.logout()
        background_brain.stop()

def launch_frontend():
    """Launch the Vite frontend server."""
    frontend_path = os.path.join(os.getcwd(), "JarvisIN", "aura-core")
    if os.path.exists(frontend_path):
        logger.info(f"Launching Vite frontend in {frontend_path}...")
        try:
            # Use shell=True for npm on Windows
            subprocess.Popen(["npm", "run", "dev"], cwd=frontend_path, shell=True)
            return True
        except Exception as e:
            logger.error(f"Failed to launch frontend: {e}")
    else:
        logger.warning("Vite frontend not found at JarvisIN/aura-core")
    return False

def main():
    logger.info("Starting JARVIS Dedicated Desktop Interface...")
    
    # 1. Start the Vite Frontend (New UI)
    has_frontend = launch_frontend()
    
    # 2. Start static HTTP server (Legacy/Fallback)
    server_thread = threading.Thread(target=_start_static_server, kwargs={"port": 8766}, daemon=True)
    server_thread.start()

    # 3. Start backend worker thread
    jarvis_thread = threading.Thread(target=jarvis_avatar_worker, daemon=True)
    jarvis_thread.start()

    # 4. Run the UI in the MAIN THREAD (Required for PyQt6)
    try:
        # Use Vite port if available, otherwise fallback to static server
        ui_url = "http://localhost:8080" if has_frontend else "http://127.0.0.1:8766/avatar/index.html"
        
        # Wait a few seconds for Vite to initialize
        if has_frontend:
            logger.info("Waiting for Vite server to initialize...")
            time.sleep(5)
            
        app, window = launch_shell(url=ui_url)
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"UI Shell crashed: {e}")
    finally:
        avatar_server_instance.stop()
        logger.info("Avatar System Shutdown Complete.")

if __name__ == '__main__':
    main()
