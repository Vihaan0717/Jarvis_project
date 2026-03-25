import asyncio
import websockets
import json
import threading
import time
from core.logger import get_logger
from agents.vision_agent import VisionTracker
from config.system_config import JarvisConfig
from services.system_watcher import SystemWatcher
from services.api_hub import APIHub
from agents.research_agent import ResearchAgent

logger = get_logger("AvatarServer")

class AvatarServer:
    def __init__(self):
        self.connected_clients = set()
        self.tracker = VisionTracker()
        self.biometric_guard = None # Set by main.py
        self.toolbox = None         # Set by main.py
        self.loop = None
        self.server = None
        self.server_thread = None
        self.tracking_thread = None
        self.running = False
        
        # New Services
        self.api_hub = APIHub()
        self.ai_agent = ResearchAgent()
        self.watcher = None # Initialized in start()

    async def _handler(self, websocket):
        logger.info("New Avatar Client Connected!")
        self.connected_clients.add(websocket)
        
        # Send initial data
        await self._send_initial_state(websocket)
        
        try:
            async for message in websocket:
                await self._handle_incoming_message(message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            logger.info("Avatar Client Disconnected.")

    async def _send_initial_state(self, websocket):
        """Send weather, news, etc. on connection."""
        data = {
            "type": "INIT_DATA",
            "weather": self.api_hub.get_weather(),
            "news": self.api_hub.get_news(),
            "movies": self.api_hub.get_movies(),
            "system_config": {
                "environment": JarvisConfig.ENVIRONMENT,
                "model": JarvisConfig.LOCAL_MODEL_NAME
            }
        }
        await websocket.send(json.dumps(data))

    async def _handle_incoming_message(self, message_str):
        try:
            data = json.loads(message_str)
            msg_type = data.get("type")
            
            if msg_type == "PROJECT_COMMAND":
                action = data.get("action")
                params = data.get("parameters", {})
                if self.toolbox:
                    result = self.toolbox.execute_tool(action, params)
                    await self._broadcast({"type": "COMMAND_RESULT", "result": result})
            
            elif msg_type == "GET_CODE_GEN":
                prompt = data.get("prompt", "Create a python script")
                logger.info(f"UI requested code for: {prompt}")
                # Calling the AI agent in a thread to not block the WebSocket loop
                def run_ai():
                    code_response = self.ai_agent.think(f"Generate a code snippet for: {prompt}. Return ONLY the code block.")
                    if self.loop and self.loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            self._broadcast({"type": "CODE_RESULT", "code": code_response}), 
                            self.loop
                        )
                threading.Thread(target=run_ai, daemon=True).start()
                
        except Exception as e:
            logger.error(f"Error handling UI message: {e}")

    def on_os_context_change(self, context):
        """Callback for SystemWatcher."""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast(context), self.loop)

    async def _broadcast(self, message: dict):
        if not self.connected_clients:
            return
        
        payload = json.dumps(message)
        websockets.broadcast(self.connected_clients, payload)

    def has_clients(self) -> bool:
        """Returns True if there is at least one active WebSocket client."""
        return len(self.connected_clients) > 0

    def trigger_animation(self, action_name: str):
        """Called by JARVIS to send an animation command to the 3D model."""
        logger.info(f"Triggering Animation: {action_name}")
        message = {
            "type": "ANIMATION",
            "action": action_name
        }
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast(message), self.loop)

    def send_ai_response(self, text: str, emotion: str = "neutral"):
        """Broadcasting AI text and emotion to the frontend."""
        logger.info(f"Broadcasting AI Response: text='{text[:50]}...', emotion='{emotion}'")
        message = {
            "type": "AI_RESPONSE",
            "text": text,
            "emotion": emotion
        }
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast(message), self.loop)

    def send_audio_command(self, audio_url: str):
        """Tells the frontend to play a specific audio file for lip-sync."""
        logger.info(f"Sending audio play command: {audio_url}")
        message = {
            "type": "PLAY_AUDIO",
            "url": audio_url
        }
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast(message), self.loop)

    def _start_tracking_loop(self):
        self.tracker.start_camera()
        while self.running:
            data = self.tracker.process_frame()
            if data and self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self._broadcast(data), self.loop)
                
                if self.biometric_guard:
                    current_time = time.time()
                    if data.get("detected") and (current_time - self.biometric_guard.last_verification_time > 60):
                        # Trigger UI Scan Animation
                        asyncio.run_coroutine_threadsafe(
                            self._broadcast({"type": "BIOMETRIC_EVENT", "status": "SCANNING"}), 
                            self.loop
                        )
                        self.biometric_guard.verify_identity(frame=self.tracker.last_frame)
            
            time.sleep(1.0 / 30.0)
        self.tracker.stop_camera()

    def _run_server(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        async def _start_server():
            self.server = await websockets.serve(self._handler, "127.0.0.1", 8765)

        self.loop.run_until_complete(_start_server())
        logger.info("WebSocket Avatar Server running on ws://127.0.0.1:8765")
        self.loop.run_forever()
        self.loop.close()

    def start(self):
        self.running = True
        
        # Start System Watcher
        self.watcher = SystemWatcher(".", self.on_os_context_change)
        self.watcher.start()
        
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        self.tracking_thread = threading.Thread(target=self._start_tracking_loop, daemon=True)
        self.tracking_thread.start()

    def stop(self):
        self.running = False
        if self.watcher:
            self.watcher.stop()
            
        if self.loop and self.loop.is_running():
            if self.server:
                self.loop.call_soon_threadsafe(self.server.close)
            self.loop.call_soon_threadsafe(self.loop.stop)
            
        if self.server_thread:
            self.server_thread.join()
        if self.tracking_thread:
            self.tracking_thread.join()

# Global singleton for JARVIS to use
avatar_server_instance = AvatarServer()

