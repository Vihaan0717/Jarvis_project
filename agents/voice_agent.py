import speech_recognition as sr
import time
import win32com.client
import pythoncom
import re
import os
import requests
import edge_tts
import asyncio
from core.logger import get_logger

logger = get_logger("VoiceAgent")

class VoiceListener:
    """JARVIS audio intake system."""
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.5
        self._mic_ready = True
        self._mic_error_logged = False
        self._mic_checked = False
        logger.info("Voice Listener initialized. Ears are open.")

    def is_available(self) -> bool:
        if self._mic_checked:
            return self._mic_ready
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            count = p.get_device_count()
            p.terminate()
            if count == 0:
                logger.error("No audio input devices found.")
                self._mic_ready = False
            else:
                _ = sr.Microphone()
                self._mic_ready = True
                logger.info(f"Microphone system active. {count} devices detected.")
        except Exception as e:
            self._mic_ready = False
            if not self._mic_error_logged:
                logger.error(f"Microphone unavailable: {e}")
                self._mic_error_logged = True
        self._mic_checked = True
        return self._mic_ready

    def listen(self, language_code: str = "en-IN", speaker=None) -> str:
        if speaker and speaker.active_speaking:
            while speaker.active_speaking:
                time.sleep(0.1)
            time.sleep(0.5)
            return ""

        if not self.is_available():
            time.sleep(2)
            return ""

        try:
            mic = sr.Microphone()
            with mic as source:
                print(f"\nJARVIS is listening ({language_code})... Speak now!")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing audio...")
                return self.recognizer.recognize_google(audio, language=language_code)
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            logger.error(f"Microphone error: {e}")
            return ""

class VoiceSpeaker:
    """JARVIS's ultra-stable direct Windows vocal cords."""
    def __init__(self):
        pythoncom.CoInitialize()
        self.engine = win32com.client.Dispatch("SAPI.SpVoice")
        self.engine.Rate = -2 
        self.engine.Volume = 100
        self.active_speaking = False
        self.audio_dir = os.path.join(os.getcwd(), "avatar", "audio")
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        logger.info(f"Voice Speaker initialized. Audio path: {self.audio_dir}")

    def speak(self, text: str, emotion: str = "neutral", force_local: bool = False, pose: str = None):
        from core.avatar_server import avatar_server_instance
        self.active_speaking = True
        try:
            clean_text = re.sub(r'[*_#`~]', '', text).encode('ascii', 'ignore').decode('ascii')
            logger.info(f"JARVIS Speaking ({emotion}) [Pose: {pose}]: '{clean_text.strip()}'")
            if pose:
                avatar_server_instance.trigger_animation(pose)

            if force_local or not avatar_server_instance.has_clients():
                avatar_server_instance.trigger_animation("TALKING")
                avatar_server_instance.send_ai_response(clean_text, emotion=emotion)
                self.engine.Speak(clean_text)
                avatar_server_instance.trigger_animation("STOP_TALKING")
                return

            filename = "jarvis_speak.wav"
            output_file = os.path.join(self.audio_dir, filename)
            web_audio_url = f"/avatar/audio/{filename}"

            # XTTSv2 attempt
            cloner_url = "http://127.0.0.1:8768/synthesize"
            success = False
            try:
                response = requests.post(cloner_url, json={"text": clean_text, "language": "en"}, timeout=15)
                if response.status_code == 200:
                    with open(output_file, "wb") as f:
                        f.write(response.content)
                    avatar_server_instance.send_audio_command(web_audio_url)
                    success = True
                else:
                    logger.error(f"XTTS Server Error: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                logger.error("XTTS Server Not Found: Ensure 'voice_cloner_server.py' is running on port 8768.")
            except requests.exceptions.Timeout:
                logger.error("XTTS Server Timeout: Synthesis taking too long. Check GPU usage.")
            except Exception as e:
                logger.error(f"XTTS Unexpected Error: {e}")

            if not success:
                try:
                    voice = "en-US-AnaNeural"
                    async def generate():
                        communicate = edge_tts.Communicate(clean_text, voice, rate="+10%")
                        await communicate.save(output_file.replace(".wav", ".mp3"))
                    asyncio.run(generate())
                    avatar_server_instance.send_audio_command(web_audio_url.replace(".wav", ".mp3"))
                    success = True
                except: pass

            if success:
                avatar_server_instance.trigger_animation("TALKING")
                avatar_server_instance.send_ai_response(clean_text, emotion=emotion)
                duration = (len(clean_text) / 15.0) + 0.5
                time.sleep(duration)
                return

            avatar_server_instance.trigger_animation("TALKING")
            avatar_server_instance.send_ai_response(clean_text, emotion=emotion)
            self.engine.Speak(clean_text)
            avatar_server_instance.trigger_animation("STOP_TALKING")
        finally:
            self.active_speaking = False
