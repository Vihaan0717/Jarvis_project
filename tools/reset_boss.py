import cv2
import os
import time

def reset_boss_photo():
    print("\n--- JARVIS: Boss Photo Setup ---")
    print("This will replace your current security photo.")
    print("Please ensure you are in a well-lit area.\n")
    
    input("Press Enter when you are ready to look at the camera...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    # Warmup
    print("Capturing in 3...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Capture multiple frames to find a good one
    for _ in range(10):
        cap.read()
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Failed to capture image.")
        return
    
    save_path = "config/known_faces/boss.jpg"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Backup old one if exists
    if os.path.exists(save_path):
        backup_path = f"config/known_faces/boss_backup_{int(time.time())}.jpg"
        os.rename(save_path, backup_path)
        print(f"Old photo backed up to {backup_path}")
    
    cv2.imwrite(save_path, frame)
    print(f"\n✅ New Boss photo saved to {save_path}")
    print("Security protocols updated. You can now restart JARVIS.")

if __name__ == "__main__":
    reset_boss_photo()
