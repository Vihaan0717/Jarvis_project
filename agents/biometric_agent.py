import cv2
import os
import threading
from deepface import DeepFace
from core.logger import get_logger
import asyncio
import time
import uuid

# Give the guard a voice in the logs
logger = get_logger("BiometricGuard")

class BiometricGuard:
    """JARVIS's eyes and strict security checkpoint."""
    
    def __init__(self, telegram_service=None):
        self.boss_image_path = "config/known_faces/boss.jpg"
        self.last_detected_mood = "neutral" 
        self.telegram_service = telegram_service
        self.is_boss = False
        self.is_logged_in = False
        self.login_time = None
        self.last_verification_time = 0
        self.last_failed_alert_time = 0 # To throttle intruder alerts
        self._lock = threading.Lock() # Prevent concurrent scans
        
        if not os.path.exists(self.boss_image_path):
            logger.warning(f"Security Alert: Boss image not found at {self.boss_image_path}!")
        else:
            logger.info("Biometric Guard initialized. Security protocols active.")

    def _safe_remove(self, file_path, retries=3, delay=0.5):
        """Attempts to delete a file with retries to handle Windows file locking."""
        if not os.path.exists(file_path):
            return

        for i in range(retries):
            try:
                os.remove(file_path)
                return
            except PermissionError:
                if i < retries - 1:
                    logger.warning(f"File locked: {file_path}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2 # Exponential backoff
                else:
                    logger.error(f"Failed to delete locked file after {retries} attempts: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
                break

    def verify_identity(self, frame=None) -> bool:
        """Takes a photo with the webcam and verifies if it is the Boss."""
        with self._lock: # Ensure only one scan happens at a time
            # --- EMERGENCY BYPASS CHECK ---
            bypass = os.getenv("SECURITY_BYPASS", "False").lower() == "true"
            if bypass:
                logger.warning("SECURITY ALERT: Biometric security bypass is ACTIVE. Access granted without scan.")
                return True

            if frame is not None:
                logger.info("Using shared frame for identity verification...")
            else:
                logger.info("Accessing webcam for identity verification...")
                
                # 1. Open the webcam and grab frames with retries
                cap = None
                for attempt in range(3):
                    cap = cv2.VideoCapture(0)
                    if cap.isOpened():
                        break
                    logger.warning(f"Failed to open camera on attempt {attempt + 1}. Retrying...")
                    time.sleep(1)
                    
                if not cap or not cap.isOpened():
                    logger.error("Failed to access the webcam after multiple attempts. Is another program using it?")
                    return False
                
                # WARMUP PHASE: Let the camera adjust auto-exposure
                logger.info("Warming up camera sensor (5 frames)...")
                for _ in range(5):
                    cap.read()
                    time.sleep(0.1)
                    
                logger.info("Capturing identity frame...")
                ret, captured_frame = cap.read()
                cap.release()
                
                if not ret:
                    logger.error("Failed to access the webcam.")
                    return False
                frame = captured_frame
                
            # 2. Save the temporary scan with a UNIQUE filename
            scan_id = str(uuid.uuid4())[:8]
            temp_path = f"config/known_faces/temp_scan_{scan_id}.jpg"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            cv2.imwrite(temp_path, frame)
            
            # 3. Analyze and compare faces
            try:
                logger.info(f"Scanning facial biometrics using VGG-Face... (Temp file: {temp_path})")
                
                # We'll use VGG-Face as it's often more forgiving with lighting.
                result = DeepFace.verify(
                    img1_path=self.boss_image_path, 
                    img2_path=temp_path,
                    model_name="VGG-Face", 
                    enforce_detection=False
                )

                # Check for Relaxed Security setting
                relaxed = os.getenv("RELAXED_SECURITY", "False").lower() == "true"
                # Configurable threshold (default 0.68)
                default_threshold = float(os.getenv("BIOMETRIC_THRESHOLD", "0.68"))
                actual_verified = result["verified"]
                dist = result.get("distance", 1.0)
                thresh = result.get("threshold", default_threshold)
                # Log distance and threshold for debugging
                logger.info(f"Biometric verification: distance={dist}, threshold={thresh}, relaxed={relaxed}")

                # If custom threshold is set, it overrides the model's default "verified" status
                if dist < default_threshold:
                    logger.info(f"Identity confirmed via CUSTOM threshold: {dist} < {default_threshold}")
                    actual_verified = True

                # If relaxed, we allow a much higher distance (up to 0.85)
                if relaxed and dist < 0.85:
                    logger.info(f"Identity confirmed via RELAXED protocols (Distance: {dist})")
                    actual_verified = True

                if actual_verified:
                    logger.info("Identity Confirmed: Welcome back, Boss.")
                    self.is_boss = True
                    self.last_verification_time = time.time()
                    
                    # --- SESSION TRACKING & ALERTS ---
                    if not self.is_logged_in:
                        self.is_logged_in = True
                        self.login_time = time.time()
                        login_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.login_time))
                        logger.info(f"Boss Logged In at {login_str}")
                        
                        if self.telegram_service and hasattr(self.telegram_service, 'loop') and self.telegram_service.loop:
                            asyncio.run_coroutine_threadsafe(
                                self.telegram_service.send_alert(f"🛡️ SECURITY: Boss verified and logged in at {login_str}"),
                                self.telegram_service.loop
                            )
                    
                    # Cleanup
                    self._safe_remove(temp_path)
                    return True
                else:
                    logger.warning(f"INTRUDER DETECTED: Facial biometrics do not match. (Distance: {dist}, Threshold: {thresh})")
                    
                    # --- REMOTE TELEGRAM AUTHORIZATION ---
                    current_time = time.time()
                    if self.telegram_service and (current_time - self.last_failed_alert_time > 300): # Alert once every 5 mins
                        if hasattr(self.telegram_service, 'loop') and self.telegram_service.loop:
                            logger.info("Requesting remote authorization via Telegram...")
                            self.last_failed_alert_time = current_time
                            
                            # Submit the async request to the Telegram event loop
                            future = asyncio.run_coroutine_threadsafe(
                                self.telegram_service.request_authorization(temp_path),
                                self.telegram_service.loop
                            )
                            
                            try:
                                # Wait for the result (blocks this worker thread, which is fine)
                                remote_approved = future.result(timeout=65) # Slightly longer than bot timeout
                                if remote_approved:
                                    logger.info("Remote authorization GRANTED via Telegram.")
                                    self.is_boss = False # It's a guest, not the boss
                                    self.last_verification_time = time.time()
                                    self._safe_remove(temp_path)
                                    return True
                                else:
                                    logger.warning("Remote authorization DENIED via Telegram.")
                            except Exception as te:
                                logger.error(f"Remote authorization failed or timed out: {te}")
                        else:
                            logger.warning("Telegram service loop not available for remote authorization.")
                    else:
                        logger.info("Intruder alert suppressed by cooldown or Telegram service missing.")

                    # Keep the failed scan as a debug image if still denied
                    debug_path = "config/known_faces/last_failed_scan.jpg"
                    if os.path.exists(temp_path):
                        try:
                            import shutil
                            shutil.copy(temp_path, debug_path)
                            logger.info(f"Failed scan saved to {debug_path} for review.")
                        except Exception as se:
                            logger.error(f"Could not save debug image: {se}")
                    
                    self._safe_remove(temp_path)
                    return False
                    
            except Exception as e:
                logger.error(f"Facial scan failed: {e}")
                self._safe_remove(temp_path)
                return False

    def logout(self):
        """Records logout event and sends alert."""
        if self.is_logged_in:
            logout_time = time.time()
            logout_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(logout_time))
            duration = logout_time - (self.login_time or logout_time)
            mins = int(duration // 60)
            
            logger.info(f"Boss Logged Out at {logout_str} (Session: {mins} mins)")
            
            if self.telegram_service and hasattr(self.telegram_service, 'loop') and self.telegram_service.loop:
                asyncio.run_coroutine_threadsafe(
                    self.telegram_service.send_alert(f"🛡️ SECURITY: Boss logged out at {logout_str}. Session duration: {mins} mins."),
                    self.telegram_service.loop
                )
            
            self.is_logged_in = False
            self.is_boss = False
            self.login_time = None

# Test the Security System directly!
if __name__ == "__main__":
    guard = BiometricGuard()
    print("\n🛡️ Initializing Biometric Security Scan...\n")
    print("Please look directly into the webcam.\n")
    
    is_boss = guard.verify_identity()
    
    if is_boss:
        print("\nJARVIS: Identity verified. Systems unlocked.")
    else:
        print("\nJARVIS: I don't know you. My boss didn't give you permission.")