"""
Hand detection module using MediaPipe.
Handles the detection and tracking of hands in video frames.
"""

import mediapipe as mp
import cv2
from config.config import (
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    STATIC_IMAGE_MODE
)


class HandDetector:
    """Detects and tracks hands using MediaPipe."""
    
    def __init__(self):
        """Initialize MediaPipe hands solution."""
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=STATIC_IMAGE_MODE,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
    
    def detect_hands(self, frame):
        """
        Detect hands in the given frame.
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            results: MediaPipe hand detection results
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        return results
    
    def draw_landmarks(self, frame, hand_landmarks):
        """
        Draw hand landmarks and connections on the frame.
        
        Args:
            frame: BGR image to draw on
            hand_landmarks: MediaPipe hand landmarks
        """
        self.mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style()
        )
    
    def close(self):
        """Release MediaPipe resources."""
        self.hands.close()

