import queue
import time
from core.logger import get_logger
from config.system_config import JarvisConfig
from core.background_brain import BackgroundBrain

# Import the Body Parts
from services.biometric_guard import BiometricGuard
from services.voice_listener import VoiceListener
from services.voice_speaker import VoiceSpeaker

# Import the Brain
from core.orchestrator import jarvis_mind

logger = get_logger("MainSystem")

# GLOBAL THREAD-SAFE COMMUNICATION CHANNEL
alert_queue = queue.Queue()

def boot_sequence(speaker):
    """Step 1: The Security Checkpoint"""
    logger.info("Initiating JARVIS Boot Sequence...")
    JarvisConfig.validate_keys()
    
    guard = BiometricGuard()
    speaker.speak("Initiating biometric security scan. Please look at the camera.")
    
    if not guard.verify_identity():
        speaker.speak("Unauthorized user detected. Locking all systems.")
        return False
        
    speaker.speak("Identity verified. Welcome back, Boss.")
    return True

def foreground_loop(speaker, listener, background_brain):
    """The Main Voice Loop (with multilingual toggle)"""
    from services.multilingual_translator import MultilingualTranslator
    translator = MultilingualTranslator()
    
    # JARVIS starts in English (India region)
    current_language = "en-IN" 
    
    speaker.speak("All systems are online and the Trinity Mind is active. How can I help you today?")
    
    while True:
        try:
            while True:  
                alert = alert_queue.get_nowait()
                logger.info(f"Background Alert Received: {alert['type']}")
                speaker.speak(alert['message'])
        except queue.Empty:
            pass  
            
        # Pass the current language code to the microphone!
        raw_input = listener.listen(language_code=current_language)
        
        if not raw_input:
            continue
            
        # 1. LANGUAGE TOGGLE COMMANDS (Always spoken in English to switch modes)
        if "switch to telugu" in raw_input.lower():
            current_language = "te-IN"
            speaker.speak("I am now listening in Telugu, Boss.")
            continue
        elif "switch to english" in raw_input.lower() or "english mode" in raw_input.lower():
            current_language = "en-IN"
            speaker.speak("Switching back to English.")
            continue
            
        # 2. TRANSLATE FOREIGN INPUT TO ENGLISH
        user_input = raw_input
        if current_language == "te-IN":
            # If he heard Telugu, he must translate it to English before thinking!
            user_input = translator.translate_to_english(raw_input, "te")
            if not user_input: continue
            
        # 3. NORMAL SHUTDOWN
        if "sleep" in user_input.lower() or "power down" in user_input.lower():
            speaker.speak("Powering down cognitive systems. Goodbye, Boss.")
            background_brain.stop() 
            break
            
        # 4. ROUTE TO MASTER ORCHESTRATOR
        try:
            logger.info("Routing voice command to the Orchestrator...")
            state = jarvis_mind.invoke({"messages": [user_input]})
            response = state['final_response']
            
            # If we are in Telugu mode, he should reply in Telugu!
            if current_language == "te-IN":
                translator.translate_and_speak(response, "telugu")
            else:
                speaker.speak(response)
            
        except Exception as e:
            logger.error(f"Brain connection error: {e}")
            speaker.speak("I'm sorry, my cognitive routing systems encountered an error.")

def run_jarvis():
    """Main entry point - spawns both threads."""
    speaker = VoiceSpeaker()
    
    if not boot_sequence(speaker):
        return
        
    listener = VoiceListener()
    
    # WAKE UP THE BACKGROUND DAEMON
    background_brain = BackgroundBrain(alert_queue)
    background_brain.start()
    
    # RUN FOREGROUND LOOP (Main Thread)
    try:
        foreground_loop(speaker, listener, background_brain)
    finally:
        background_brain.stop() # Failsafe shutdown

if __name__ == "__main__":
    run_jarvis()