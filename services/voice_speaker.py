import win32com.client
import pythoncom
import re
import os
import requests
import edge_tts
import asyncio
from core.logger import get_logger

logger = get_logger("VoiceSpeaker")

class VoiceSpeaker:
    """JARVIS's ultra-stable direct Windows vocal cords."""
    
    def __init__(self):
        pythoncom.CoInitialize()
        self.engine = win32com.client.Dispatch("SAPI.SpVoice")
        self.engine.Rate = -2 
        self.engine.Volume = 100
        # For coordination with VoiceListener
        self.active_speaking = False
        # Ensure the audio directory exists for the web server
        self.audio_dir = os.path.join(os.getcwd(), "avatar", "audio")
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        logger.info(f"Voice Speaker initialized. Audio path: {self.audio_dir}")

    def speak(self, text: str, emotion: str = "neutral", force_local: bool = False, pose: str = None):
        """Converts text into offline audible speech and notifies the Avatar."""
        from core.avatar_server import avatar_server_instance
        self.active_speaking = True
        
        try:
            # 1. Cleaning text for TTS engines
            clean_text = re.sub(r'[*_#`~]', '', text)
            clean_text = clean_text.encode('ascii', 'ignore').decode('ascii')
            
            logger.info(f"JARVIS Speaking ({emotion}) [Pose: {pose}]: '{clean_text.strip()}'")
            
            if pose:
                avatar_server_instance.trigger_animation(pose)
            
            # (Triggers moved below to sync with audio generation)

            # FALLBACK CHECK: If no browser is connected yet, we MUST use direct Windows speakers
            if force_local or not avatar_server_instance.has_clients():
                if not force_local:
                    logger.info("No browser clients detected. Forcing local computer speakers.")
                avatar_server_instance.trigger_animation("TALKING")
                avatar_server_instance.send_ai_response(clean_text, emotion=emotion)
                self.engine.Speak(clean_text)
                avatar_server_instance.trigger_animation("STOP_TALKING")
                return

            filename = "jarvis_speak.wav"
            output_file = os.path.join(self.audio_dir, filename)
            web_audio_url = f"/avatar/audio/{filename}"

            # 3. ATTEMPT 1: LOCAL XTTSv2 CLONER (Anime Voice) with retries
            cloner_url = "http://127.0.0.1:8768/synthesize"
            success = False
            for attempt in range(3):
                try:
                    response = requests.post(cloner_url, json={"text": clean_text, "language": "en"}, timeout=10)
                    if response.status_code == 200:
                        with open(output_file, "wb") as f:
                            f.write(response.content)
                        avatar_server_instance.send_audio_command(web_audio_url)
                        success = True
                        break
                except Exception:
                    if attempt < 2:
                        import time
                        time.sleep(1)
            
            # (duration wait handled below)

            # 4. ATTEMPT 2: EDGE-TTS (Cute Anime fallback)
            try:
                voice = "en-US-AnaNeural"
                async def generate():
                    communicate = edge_tts.Communicate(clean_text, voice, rate="+10%")
                    await communicate.save(output_file.replace(".wav", ".mp3"))
                asyncio.run(generate())
                
                avatar_server_instance.send_audio_command(web_audio_url.replace(".wav", ".mp3"))
                success = True
            except Exception as e:
                logger.warning(f"Edge-TTS failed: {e}. Falling back to SAPI5.")

            if success:
                # SYNCED TRIGGER: Subtitles and Animation start with Audio
                avatar_server_instance.trigger_animation("TALKING")
                avatar_server_instance.send_ai_response(clean_text, emotion=emotion)
                
                # ANTI-ECHO DURATION WAIT
                # Average reading speed is ~15 chars per sec. chars / 15 + overhead
                duration = (len(clean_text) / 15.0) + 0.5
                logger.info(f"Holding microphone lock for {duration:.2f}s during browser playback.")
                import time
                time.sleep(duration)
                return

            # 5. FINAL FALLBACK: SAPI5 (Direct Windows Voice)
            avatar_server_instance.trigger_animation("TALKING")
            avatar_server_instance.send_ai_response(clean_text, emotion=emotion)
            self.engine.Speak(clean_text)
            avatar_server_instance.trigger_animation("STOP_TALKING")
        finally:
            self.active_speaking = False

# Test the vocal cords directly!
if __name__ == "__main__":
    mouth = VoiceSpeaker()
    print("\n🗣️ Testing Audio Output...\n")
    mouth.speak("Hello Boss. My direct Windows vocal systems are fully operational.")
