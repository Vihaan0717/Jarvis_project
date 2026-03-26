import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import math
import time
import os
from core.logger import get_logger

logger = get_logger("VisionTracker")

class VisionTracker:
    def __init__(self):
        # We use the new MediaPipe Tasks API for v0.10+
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'avatar', 'face_landmarker.task')
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=1
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        
        # Jitter reduction: Store last values for low-pass filtering
        self.last_pose = {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
        self.smoothing_factor = 0.1 # Lower = smoother to avoid high-FPS shaking
        
        self.cap = None
        self.is_running = False
        self.master_detected = False
        self.last_frame = None # Store the latest raw frame for biometric sharing

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.is_running = True
        logger.info("Vision Tracker Camera Started")

    def stop_camera(self):
        self.is_running = False
        if self.detector:
            self.detector.close()
        if self.cap:
            self.cap.release()
        logger.info("Vision Tracker Camera Stopped")

    def _get_head_pose_from_matrix(self, matrix):
        """Extracts Euler angles (Pitch, Yaw, Roll) from the Transformation Matrix"""
        # The matrix is 4x4. We extract the 3x3 rotation matrix
        rotation_matrix = matrix[:3, :3]
        
        # Calculate Euler angles from rotation matrix
        sy = np.sqrt(rotation_matrix[0, 0] * rotation_matrix[0, 0] +  rotation_matrix[1, 0] * rotation_matrix[1, 0])
        singular = sy < 1e-6

        if not singular:
            x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            y = math.atan2(-rotation_matrix[2, 0], sy)
            z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            x = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            y = math.atan2(-rotation_matrix[2, 0], sy)
            z = 0

        # Convert to degrees for easier debugging
        x_deg = np.degrees(x)
        y_deg = np.degrees(y)
        z_deg = np.degrees(z)
        
        # VRM rotation values are usually in radians. 
        # We send a value that app.js will scale or use directly.
        # Standard head range is roughly +/- 45 degrees (0.78 rad).
        
        # MODIFIED: Removed the 180 shift which was likely causing the "switched head" issue.
        # Yaw (Left/Right), Pitch (Up/Down), Roll (Tilt)
        # Increased clamps to 2.0 and lower shrink from 0.02 to 0.015 to allow maximum rotation bandwidth
        # Calculate multipliers (MediaPipe output is very small ~0-1.5, we want bigger range)
        # We increase mult to 0.035 for dynamic head tracking range
        pose_raw = {
            "pitch": max(min(x_deg * 0.035, 2.0), -2.0), 
            "yaw": max(min(y_deg * 0.035, 2.0), -2.0),
            "roll": max(min(z_deg * 0.035, 2.0), -2.0)
        }

        # Apply Low-Pass Filter
        for key in self.last_pose:
            self.last_pose[key] = (self.last_pose[key] * (1 - self.smoothing_factor)) + (pose_raw[key] * self.smoothing_factor)
        
        return self.last_pose

    def process_frame(self):
        if not self.cap or not self.cap.isOpened():
            return None

        success, image = self.cap.read()
        if not success:
            # Throttle warnings to once every 5 seconds to prevent console spam
            current_time = time.time()
            if not hasattr(self, '_last_warning_time') or (current_time - self._last_warning_time > 5):
                logger.warning("Empty camera frame. Camera may be in use by another module.")
                self._last_warning_time = current_time
            return None

        # Store ORIGINAL non-mirrored frame for Biometrics (better deepface accuracy)
        self.last_frame = image.copy() 
        
        # MediaPipe requires RGB images and flipping for a mirror effect on the Avatar
        image = cv2.flip(image, 1)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Detect
        results = self.detector.detect(mp_image)

        tracking_data = {
            "type": "TRACKING",
            "pitch": 0, "yaw": 0, "roll": 0,
            "blink_left": 0, "blink_right": 0,
            "eye_pitch": 0, "eye_yaw": 0,
            "detected": False,
            "user_emotion": "neutral", "emotion_intensity": 0.0
        }

        if results.face_blendshapes and len(results.face_blendshapes) > 0:
            tracking_data["detected"] = True
            blendshapes = results.face_blendshapes[0]
            
            # Extract Blinks, Eye Gaze, and User Emotion Blendshapes
            smile_l, smile_r, brow_up = 0.0, 0.0, 0.0
            for category in blendshapes:
                name = category.category_name
                score = category.score
                if name == "eyeBlinkLeft":     tracking_data["blink_left"] = min(score * 2.5, 1.0)
                elif name == "eyeBlinkRight":  tracking_data["blink_right"] = min(score * 2.5, 1.0)
                elif name == "mouthSmileLeft": smile_l = score
                elif name == "mouthSmileRight": smile_r = score
                elif name == "browInnerUp":    brow_up = score
                # Eye Gaze (Compute relative spherical angles instead of accumulating)
                if name == "eyeLookUpLeft":    tracking_data["eye_pitch"] -= score * 0.3
                elif name == "eyeLookDownLeft":  tracking_data["eye_pitch"] += score * 0.3
                elif name == "eyeLookInLeft":    tracking_data["eye_yaw"]   += score * 0.4
                elif name == "eyeLookOutLeft":   tracking_data["eye_yaw"]   -= score * 0.4
                elif name == "eyeLookUpRight":   tracking_data["eye_pitch"] -= score * 0.3
                elif name == "eyeLookDownRight": tracking_data["eye_pitch"] += score * 0.3
                elif name == "eyeLookInRight":   tracking_data["eye_yaw"]   -= score * 0.4
                elif name == "eyeLookOutRight":  tracking_data["eye_yaw"]   += score * 0.4

            # Derive user emotion from facial signals
            avg_smile = (smile_l + smile_r) / 2.0
            if avg_smile > 0.35:
                tracking_data["user_emotion"] = "happy"
                tracking_data["emotion_intensity"] = min(avg_smile * 1.5, 1.0)
            elif brow_up > 0.4:
                tracking_data["user_emotion"] = "worried"
                tracking_data["emotion_intensity"] = min(brow_up * 1.2, 1.0)

        if results.facial_transformation_matrixes and len(results.facial_transformation_matrixes) > 0:
            matrix = results.facial_transformation_matrixes[0]
            pose = self._get_head_pose_from_matrix(matrix)
            tracking_data["pitch"] = pose["pitch"]
            tracking_data["yaw"] = pose["yaw"]
            tracking_data["roll"] = pose["roll"]

        return tracking_data
