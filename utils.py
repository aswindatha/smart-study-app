import cv2
import mediapipe as mp
import numpy as np
import base64
import math
from typing import Tuple, List, Optional
from collections import deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- INIT --------------------
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# -------------------- LANDMARKS --------------------
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
LEFT_EYE_POINTS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_POINTS = [362, 385, 387, 263, 373, 380]

class CleanAnalyticsTracker:
    """
    Clean and efficient learning analytics tracker based on cog_anltycs.py
    """
    def __init__(self, buffer_size=8, confidence_threshold=0.5):
        self.buffer_size = buffer_size
        self.confidence_threshold = confidence_threshold
        
        # Initialize MediaPipe Face Mesh
        try:
            self.face_mesh = mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=confidence_threshold,
                min_tracking_confidence=confidence_threshold
            )
            logger.info("MediaPipe Face Mesh initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MediaPipe Face Mesh: {e}")
            self.face_mesh = None
        
        # -------------------- SMOOTHING --------------------
        self.gaze_buffer = deque(maxlen=buffer_size)
        self.attention_buffer = deque(maxlen=buffer_size)
        self.load_buffer = deque(maxlen=buffer_size)
        self.engagement_buffer = deque(maxlen=buffer_size)
        
        # Fallback values
        self.last_valid_gaze = 50.0
        self.last_valid_attention = 50.0
        self.last_valid_cognitive = 30.0
        self.last_valid_engagement = 40.0
    
    def get_point(self, landmarks, idx, w, h):
        """Get landmark point as numpy array"""
        return np.array([int(landmarks[idx].x * w), int(landmarks[idx].y * h)])
    
    def distance(self, p1, p2):
        """Calculate distance between two points"""
        return np.linalg.norm(p1 - p2)
    
    def compute_ear(self, landmarks, eye_points, w, h):
        """Compute Eye Aspect Ratio for blink detection"""
        p1 = self.get_point(landmarks, eye_points[0], w, h)
        p2 = self.get_point(landmarks, eye_points[1], w, h)
        p3 = self.get_point(landmarks, eye_points[2], w, h)
        p4 = self.get_point(landmarks, eye_points[3], w, h)
        p5 = self.get_point(landmarks, eye_points[4], w, h)
        p6 = self.get_point(landmarks, eye_points[5], w, h)

        vertical1 = self.distance(p2, p6)
        vertical2 = self.distance(p3, p5)
        horizontal = self.distance(p1, p4)

        if horizontal == 0:
            return 0.3  # Default value
        
        return (vertical1 + vertical2) / (2.0 * horizontal)
    
    def iris_center(self, landmarks, iris_idx, w, h):
        """Calculate iris center from iris landmarks"""
        pts = [self.get_point(landmarks, i, w, h) for i in iris_idx]
        return np.mean(pts, axis=0)
    
    def smooth(self, buffer, value):
        """Apply smoothing using moving average"""
        buffer.append(value)
        return sum(buffer) / len(buffer)
    
    def analyze_frame(self, img: np.ndarray, student_cognitive_limit: int = 50) -> Tuple[float, float, float, float, bool]:
        """
        Analyze a single frame for learning analytics
        Returns: (gaze_score, attention_score, cognitive_load, engagement, face_detected)
        """
        if self.face_mesh is None:
            logger.error("MediaPipe Face Mesh not initialized")
            return self.get_fallback_values()
        
        h, w, _ = img.shape
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        # Default values
        gaze_score = 0
        attention_score = 0
        cognitive_load = 100
        engagement = 0
        face_detected = False

        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0].landmark
            face_detected = True

            # -------- EAR --------
            ear_left = self.compute_ear(face, LEFT_EYE_POINTS, w, h)
            ear_right = self.compute_ear(face, RIGHT_EYE_POINTS, w, h)
            ear = (ear_left + ear_right) / 2.0

            eye_opening = np.clip((ear - 0.15) / (0.35 - 0.15), 0, 1)

            # -------- BLINK --------
            blink = ear < 0.18

            # -------- HEAD POSE --------
            nose = self.get_point(face, 1, w, h)
            yaw = (nose[0] - w / 2) / w * 100
            pitch = (nose[1] - h / 2) / h * 100
            head_penalty = min(25, (abs(yaw) + abs(pitch)) / 2.5)

            # -------- METRICS --------
            gaze_score = eye_opening * 100

            attention_score = eye_opening * 100
            if blink:
                attention_score -= 30
            attention_score -= head_penalty
            attention_score = np.clip(attention_score, 0, 100)

            cognitive_load = (1 - eye_opening) * 80 + 10
            cognitive_load = np.clip(cognitive_load, 10, 95)

            engagement = attention_score * 0.9
            engagement = np.clip(engagement, 5, 100)

            # -------- SMOOTH --------
            gaze_score = self.smooth(self.gaze_buffer, gaze_score)
            attention_score = self.smooth(self.attention_buffer, attention_score)
            cognitive_load = self.smooth(self.load_buffer, cognitive_load)
            engagement = self.smooth(self.engagement_buffer, engagement)

            # Update fallback values
            self.last_valid_gaze = gaze_score
            self.last_valid_attention = attention_score
            self.last_valid_cognitive = cognitive_load
            self.last_valid_engagement = engagement

            logger.info(f"Face detected - Gaze: {gaze_score:.1f}%, Attention: {attention_score:.1f}%, "
                       f"Cognitive: {cognitive_load:.1f}%, Engagement: {engagement:.1f}%")
        else:
            logger.info("No face detected")
            return self.get_fallback_values()

        return gaze_score, attention_score, cognitive_load, engagement, face_detected
    
    def get_fallback_values(self) -> Tuple[float, float, float, float, bool]:
        """Get last known valid values when no face detected"""
        return (
            self.last_valid_gaze,
            self.last_valid_attention,
            self.last_valid_cognitive,
            self.last_valid_engagement,
            False
        )
    
    def draw_debug_overlay(self, img: np.ndarray, gaze_score: float, attention_score: float, 
                          cognitive_load: float, engagement: float, face_detected: bool) -> np.ndarray:
        """Draw debug overlay with metrics visualization"""
        overlay_img = img.copy()
        
        def draw_bar(y, label, value, color):
            cv2.putText(overlay_img, f"{label}: {int(value)}%", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.rectangle(overlay_img, (150, y - 15),
                         (150 + int(value * 2), y - 5), color, -1)

        draw_bar(30, "Gaze", gaze_score, (0, 255, 0))
        draw_bar(60, "Attention", attention_score, (255, 255, 0))
        draw_bar(90, "Cognitive Load", cognitive_load, (0, 0, 255))
        draw_bar(120, "Engagement", engagement, (255, 0, 255))
        
        # Add face detection status
        status_text = "Face Detected" if face_detected else "No Face"
        status_color = (0, 255, 0) if face_detected else (0, 0, 255)
        cv2.putText(overlay_img, status_text, (10, 160), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        return overlay_img

# Global tracker instance
clean_tracker = CleanAnalyticsTracker()

def analyze_face_from_image(image_data: str, student_cognitive_limit: int = 50) -> Tuple[float, float, float, float, bool]:
    """
    Main face analysis function using clean analytics approach
    Returns: (gaze_score, attention_score, cognitive_load, engagement_level, face_detected)
    All scores are in 0-100 range
    """
    try:
        # Decode image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return clean_tracker.get_fallback_values()
        
        # Analyze using clean tracker
        return clean_tracker.analyze_frame(img, student_cognitive_limit)
        
    except Exception as e:
        logger.error(f"Error in face analysis: {e}")
        return clean_tracker.get_fallback_values()

def analyze_face_with_debug_overlay(image_data: str, student_cognitive_limit: int = 50) -> \
        Tuple[float, float, float, float, bool, str]:
    """
    Analyze face with debug overlay using clean analytics
    Returns: (gaze, attention, cognitive, engagement, face_detected, debug_image_base64)
    """
    try:
        # Perform regular analysis
        gaze, attention, cognitive, engagement, face_detected = analyze_face_from_image(
            image_data, student_cognitive_limit)
        
        # Generate debug overlay
        debug_image_base64 = ""
        if face_detected:
            # Decode image for overlay
            image_data_clean = image_data.split(',')[1] if ',' in image_data else image_data
            image_bytes = base64.b64decode(image_data_clean)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is not None:
                # Draw overlay
                debug_img = clean_tracker.draw_debug_overlay(
                    img, gaze, attention, cognitive, engagement, face_detected)
                
                # Convert back to base64
                _, buffer = cv2.imencode('.jpg', debug_img)
                debug_image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return gaze, attention, cognitive, engagement, face_detected, debug_image_base64
        
    except Exception as e:
        logger.error(f"Error in face analysis with debug: {e}")
        gaze, attention, cognitive, engagement, _ = clean_tracker.get_fallback_values()
        return gaze, attention, cognitive, engagement, False, ""

# Legacy functions for backward compatibility
def calculate_cognitive_load(gaze_score: float, student_cognitive_limit: int) -> float:
    """Legacy cognitive load calculation"""
    return (100 - gaze_score) * 0.8 + 10

def calculate_engagement(attention_score: float) -> float:
    """Legacy engagement calculation"""
    return attention_score * 0.9 + 5

def calculate_cognitive_load_legacy(gaze_score: float, student_cognitive_limit: int) -> Tuple[float, str]:
    """Legacy cognitive load with emotional state"""
    cognitive_load = calculate_cognitive_load(gaze_score, student_cognitive_limit)
    
    if cognitive_load > student_cognitive_limit * 1.2:
        emotional_state = "overwhelmed"
    elif cognitive_load > student_cognitive_limit:
        emotional_state = "stressed"
    elif cognitive_load > student_cognitive_limit * 0.6:
        emotional_state = "focused"
    else:
        emotional_state = "relaxed"
    
    return cognitive_load, emotional_state

def calculate_engagement_legacy(face_attention_score: float) -> float:
    """Legacy engagement calculation"""
    return calculate_engagement(face_attention_score)

# For backward compatibility with existing code
stable_tracker = clean_tracker
