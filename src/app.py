"""
Main application orchestrator.
Coordinates hand detection, gesture recognition, and visualization.
"""

import cv2
from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.visualizer import Visualizer
from src.mouse_controller import MouseController
from config.config import (
    CAMERA_INDEX, 
    MIRROR_VIEW, 
    WINDOW_NAME,
    ENABLE_MOUSE_CONTROL
)


class HandGestureApp:
    """Main application class that coordinates all components."""
    
    def __init__(self, enable_mouse_control=None):
        """
        Initialize the application components.
        
        Args:
            enable_mouse_control: Enable mouse control with gestures (None = use config)
        """
        if enable_mouse_control is None:
            enable_mouse_control = ENABLE_MOUSE_CONTROL
            
        self.detector = HandDetector()
        self.recognizer = GestureRecognizer()
        self.visualizer = Visualizer()
        self.mouse_controller = MouseController() if enable_mouse_control else None
        self.cap = None
        self.enable_mouse_control = enable_mouse_control
    
    def initialize_camera(self):
        """
        Initialize the camera.
        
        Returns:
            bool: True if camera opened successfully, False otherwise
        """
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera at index {CAMERA_INDEX}")
            return False
        
        return True
    
    def process_frame(self, frame):
        """
        Process a single frame: detect hands and recognize gestures.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (processed_frame, gestures_list)
        """

        if MIRROR_VIEW:
            frame = cv2.flip(frame, 1)

        results = self.detector.detect_hands(frame)
        
        gestures = []
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, 
                results.multi_handedness
            ):

                self.detector.draw_landmarks(frame, hand_landmarks)
                
                hand_label = handedness.classification[0].label
                confidence = handedness.classification[0].score
                
                gesture_info = self.recognizer.recognize_gesture(
                    hand_landmarks.landmark,
                    hand_label
                )
                
                # Execute mouse control action if enabled
                action_result = 'none'
                if self.enable_mouse_control and self.mouse_controller:
                    action_result = self.mouse_controller.execute_action(
                        gesture_info,
                        hand_landmarks.landmark,
                        frame.shape
                    )
                
                gestures.append({
                    'hand': hand_label,
                    'gesture': gesture_info['name'],
                    'action': action_result,
                    'confidence': confidence
                })

        self.visualizer.draw_gesture_text(frame, gestures)
        
        return frame, gestures
    
    def run(self):
        """Main application loop."""

        if not self.initialize_camera():
            return
        
        self.visualizer.print_welcome_message()
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            processed_frame, gestures = self.process_frame(frame)
            
            self.visualizer.print_gestures(gestures)
            
            cv2.imshow(WINDOW_NAME, processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
    
    def cleanup(self):
        """Release resources and cleanup."""
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        self.detector.close()
        self.visualizer.print_exit_message()

