import cv2
import os
from deepface import DeepFace
from core.logger import get_logger

# Give the guard a voice in the logs
logger = get_logger("BiometricGuard")

class BiometricGuard:
    """JARVIS's eyes and strict security checkpoint."""
    
    def __init__(self):
        self.boss_image_path = "config/known_faces/boss.jpg"
        
        if not os.path.exists(self.boss_image_path):
            logger.warning(f"Security Alert: Boss image not found at {self.boss_image_path}!")
        else:
            logger.info("Biometric Guard initialized. Security protocols active.")

    def verify_identity(self) -> bool:
        """Takes a photo with the webcam and verifies if it is the Boss."""
        logger.info("Accessing webcam for identity verification...")
        
        # 1. Open the webcam and grab a single frame
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logger.error("Failed to access the webcam.")
            return False
            
        # 2. Save the temporary scan
        temp_path = "config/known_faces/temp_scan.jpg"
        cv2.imwrite(temp_path, frame)
        
        # 3. Analyze and compare faces
        try:
            logger.info("Scanning facial biometrics. This may take a moment...")
            
            # DeepFace compares the webcam snapshot to your saved boss.jpg
            result = DeepFace.verify(img1_path=self.boss_image_path, img2_path=temp_path)
            
            # Clean up the temporary file so it doesn't clutter your drive
            os.remove(temp_path)
            
            if result["verified"]:
                logger.info("Identity Confirmed: Welcome back, Boss.")
                return True
            else:
                logger.warning("INTRUDER DETECTED: Facial biometrics do not match.")
                return False
                
        except Exception as e:
            logger.error(f"Facial scan failed: {e}")
            return False

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