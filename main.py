from core.logger import get_logger
from config.system_config import JarvisConfig

# Import the Body Parts
from services.biometric_guard import BiometricGuard
from services.voice_listener import VoiceListener
from services.voice_speaker import VoiceSpeaker

# Import the Brain
from core.orchestrator import jarvis_mind

logger = get_logger("MainSystem")

# Notice how we pass 'speaker' in the parentheses now!
def boot_sequence(speaker):
    """Step 1: The Security Checkpoint"""
    logger.info("Initiating JARVIS Boot Sequence...")
    JarvisConfig.validate_keys()
    
    guard = BiometricGuard()
    
    speaker.speak("Initiating biometric security scan. Please look at the camera.")
    
    # Check if the face matches the Boss
    if not guard.verify_identity():
        speaker.speak("Unauthorized user detected. Locking all systems.")
        return False
        
    speaker.speak("Identity verified. Welcome back, Boss.")
    return True

def run_jarvis():
    """Step 2: The Continuous Conversational Loop"""
    
    # 1. We build his mouth EXACTLY ONCE right here at the start
    speaker = VoiceSpeaker()
    
    # 2. We hand the mouth to the boot sequence so it can use it
    if not boot_sequence(speaker):
        return
        
    listener = VoiceListener()
    
    speaker.speak("All systems are online and the Trinity Mind is active. How can I help you today?")
    
    # The Heartbeat Loop
    while True:
        user_input = listener.listen()
        
        if not user_input:
            continue 
            
        if "sleep" in user_input.lower() or "power down" in user_input.lower():
            speaker.speak("Powering down cognitive systems. Goodbye, Boss.")
            break
            
        try:
            logger.info("Routing voice command to the Orchestrator...")
            
            state = jarvis_mind.invoke({"messages": [user_input]})
            response = state['final_response']
            
            speaker.speak(response)
            
        except Exception as e:
            logger.error(f"Brain connection error: {e}")
            speaker.speak("I'm sorry, my cognitive routing systems encountered an error.")

if __name__ == "__main__":
    run_jarvis()