import queue
import time
import random
import asyncio
import threading
import json # Added for json.load in presence_callback
from core.logger import get_logger
from config.system_config import JarvisConfig
from core.background_brain import BackgroundBrain

# Import the Body Parts
from agents.biometric_agent import BiometricGuard
from agents.voice_agent import VoiceListener
from agents.voice_agent import VoiceSpeaker

# Import the Brain
from core import orchestrator
from core.orchestrator import jarvis_mind, process_telegram_command, telegram_service_instance
from context.context_monitor import ContextMonitor
from agents.messaging_agent import MessagingAgent
from core.telegram_service import TelegramService
from core.avatar_server import avatar_server_instance

logger = get_logger("MainSystem")

# GLOBAL THREAD-SAFE COMMUNICATION CHANNEL
from services.api_hub import APIHub

alert_queue = queue.Queue()
api_hub = APIHub()

PROACTIVE_QUESTIONS = [
    "How is your project coming along today?",
    "Anything interesting on your schedule for this evening?",
    "Have you had enough water today, Boss?",
    "The system is running at peak efficiency. Shall we tackle something ambitious?",
    "I've been monitoring the global news trends. Would you like a briefing?",
    "There's a lot of activity in the tech sector today. Ready to dive in?",
    "You've been working hard. Should I set a reminder for a break soon?",
    "The weather seems perfect for a walk later. Just a thought."
]

def get_time_based_greeting():
    """Returns a greeting based on the current hour."""
    hour = time.localtime().tm_hour
    if 5 <= hour < 12:
        return "Good morning, Boss."
    elif 12 <= hour < 18:
        return "Good afternoon, Boss."
    elif 18 <= hour < 22:
        return "Good evening, Boss."
    else:
        return "Working late, I see. Good to see you, Boss."

def boot_sequence(speaker, guard=None, telegram_service=None):
    """Step 1: The Security Checkpoint"""
    logger.info("Initiating JARVIS Boot Sequence...")
    JarvisConfig.validate_keys()
    
    if not guard:
        from agents.biometric_agent import BiometricGuard
        guard = BiometricGuard()
        
    # Force local speaker for boot so it's audible before browser connects
    speaker.speak("Initiating biometric security scan. Please look at the camera.", force_local=True)
    
    shared_frame = getattr(avatar_server_instance.tracker, 'last_frame', None) if 'avatar_server_instance' in globals() else None
    if not guard.verify_identity(frame=shared_frame):
        speaker.speak("Unauthorized user detected. Locking all systems.", force_local=True)
        return False
        
    # --- INTELLIGENT GREETING & PROACTIVE INTERROGATION ---
    greeting = get_time_based_greeting()
    question = random.choice(PROACTIVE_QUESTIONS)
    mood = guard.last_detected_mood
    
    if mood in ["sad", "angry", "fear"]:
        speaker.speak(f"{greeting} You look a bit {mood} today... is everything alright?", force_local=True)
    else:
        speaker.speak(f"{greeting}", force_local=True)
    
    # --- PROACTIVE BRIEFING & TASKING ---
    provide_briefing(speaker)
    
    question = random.choice(PROACTIVE_QUESTIONS)
    speaker.speak(question, force_local=True)
    
    return True

def provide_briefing(speaker: VoiceSpeaker):
    """JARVIS provides a summary of weather, news, and movies."""
    logger.info("Generating proactive briefing for Hyderabad...")
    
    # Weather
    weather = api_hub.get_weather("Hyderabad,IN")
    weather_desc = weather.get('description', 'clear')
    temp = weather.get('temperature', 25)
    weather_text = f"The weather in Hyderabad is {weather_desc} with a temperature of {temp} degrees Celsius."
    
    # News (Prioritize India/Tech/Politics)
    filt_news = api_hub.get_filtered_news(keywords=["India", "IT", "tech", "AI", "politics", "war"])
    if not filt_news: 
        filt_news = api_hub.get_news()[:2]
    
    news_titles = [n['title'] for n in filt_news[:3]]
    news_text = f"Main headlines include: {'; '.join(news_titles)}."
    
    # Movies (Optional)
    movies = api_hub.get_movies()[:2]
    movie_titles = [m['title'] for m in movies]
    movie_text = f"Trending movies are {', '.join(movie_titles)}."
    
    briefing = f"Here is your morning briefing, Boss. {weather_text} {news_text} {movie_text} I am monitoring for any urgent IT or political developments."
    speaker.speak(briefing, force_local=True)

def foreground_loop(speaker, listener, background_brain, guard=None, telegram_service=None, skip_greeting=False):
    """The Main Voice Loop (with robust multilingual toggle and mirroring)"""
    from agents.translation_agent import MultilingualTranslator
    translator = MultilingualTranslator()
    
    # JARVIS starts in English (India region)
    current_language = "en-IN" 
    
    if not skip_greeting:
        speaker.speak("All systems are online and the Trinity Mind is active. How can I help you today?")
    
    while True:
        try:
            while True:  
                alert = alert_queue.get_nowait()
                logger.info(f"Background Alert Received: {alert['type']}")
                speaker.speak(alert['message'])
        except queue.Empty:
            pass  
            
        try:
            # --- PERIODIC IDENTITY RE-VERIFICATION ---
            if guard and (time.time() - guard.last_verification_time > 300): # Every 5 minutes or on change
                logger.info("Performing periodic security re-verification...")
                # We don't block too long here, just a check
                # Pass the latest frame if the avatar tracker is running to avoid camera conflicts
                shared_frame = getattr(avatar_server_instance.tracker, 'last_frame', None)
                if not guard.verify_identity(frame=shared_frame):
                    logger.warning("Active session re-verification failed.")
                    # If it fails, JARVIS should ask for re-auth if someone talks
            
            raw_input = listener.listen(language_code=current_language, speaker=speaker)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Exiting foreground loop.")
            break
        if not raw_input: continue
            
        # --- 1. TRANSLATE FIRST (If in foreign mode) ---
        if current_language == "te-IN":
            user_input = translator.translate_to_english(raw_input, "te")
            if not user_input: continue
        else:
            user_input = raw_input
            
        # --- 2. PHONETIC OVERRIDE ---
        # Catch all the weird ways the mic mishears your name!
        user_input = user_input.lower().replace("javid", "jarvis").replace("javed", "jarvis").replace("jobs", "jarvis").replace("javez", "jarvis")
        
        # --- 3. ROBUST LANGUAGE TOGGLE ---
        # Checks if "telugu" and any action word is in the sentence
        if "telugu" in user_input and any(word in user_input for word in ["switch", "change", "speak"]):
            current_language = "te-IN"
            speaker.speak("I am now listening in Telugu, Boss.")
            continue
            
        # Checks if "english" and any action word is in the sentence
        elif "english" in user_input and any(word in user_input for word in ["switch", "change", "back", "mode"]):
            current_language = "en-IN"
            speaker.speak("Switching back to English.")
            continue
            
        # --- 4. NORMAL SHUTDOWN ---
        if "sleep" in user_input or "power down" in user_input:
            speaker.speak("Powering down cognitive systems. Goodbye, Boss.")
            if guard: guard.logout()
            background_brain.stop() 
            break
            
        # --- 5. ROUTE TO MASTER ORCHESTRATOR ---
        try:
            logger.info("Routing voice command to the Orchestrator...")
            state = jarvis_mind.invoke({"messages": [user_input]})
            response = state['final_response']
            emotion = state.get('emotion', 'neutral')
            pose = state.get('pose')
            
            if current_language == "te-IN":
                translator.translate_and_speak(response, "telugu")
            else:
                speaker.speak(response, emotion=emotion, pose=pose)
            
            # --- SHADOWING / MIRRORING TO TELEGRAM ---
            if telegram_service and guard and not guard.is_boss:
                shadow_msg = f"👁️ MONITORING: Guest Interface\nUser: {user_input}\nJARVIS: {response}"
                asyncio.run_coroutine_threadsafe(
                    telegram_service.send_alert(shadow_msg),
                    telegram_service.loop
                )
            
        except Exception as e:
            logger.error(f"Brain connection error: {e}")
            speaker.speak("I'm sorry, my cognitive routing systems encountered an error.")

def run_jarvis():
    """Main entry point - spawns both threads."""
    speaker = VoiceSpeaker()
    
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
    
    # --- NOW DO THE SECURITY CHECK ---
    guard = BiometricGuard(telegram_service=telegram_service)
    avatar_server_instance.biometric_guard = guard
    avatar_server_instance.toolbox = orchestrator.hands.toolbox # Provide toolbox for direct UI actions
    
    if not boot_sequence(speaker, guard=guard):
        return
        
    listener = VoiceListener()
    
    # 4. Context & Messaging (Intelligence Layer)
    context_monitor = ContextMonitor()
    context_monitor.start()
    
    messaging_agent = MessagingAgent()
    def start_messaging_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Use a callback to check presence dynamically
        loop.run_until_complete(messaging_agent.monitor(
            telegram_service=telegram_service,
            presence_callback=lambda: context_monitor.get_user_idle_time() > 120 and "Away" or "Home"
        ))

    messaging_thread = threading.Thread(target=start_messaging_loop, daemon=True)
    messaging_thread.start()
    
    # 5. WAKE UP THE BACKGROUND DAEMON
    background_brain = BackgroundBrain(alert_queue)
    background_brain.start()
    
    # RUN FOREGROUND LOOP (Main Thread)
    try:
        # Pass skip_greeting=True because boot_sequence already handled the greeting
        foreground_loop(speaker, listener, background_brain, guard=guard, telegram_service=telegram_service, skip_greeting=True)
    finally:
        if guard: guard.logout()
        background_brain.stop() # Failsafe shutdown
        if telegram_service:
            asyncio.run_coroutine_threadsafe(telegram_service.stop(), telegram_service.loop)

if __name__ == "__main__":
    run_jarvis()
