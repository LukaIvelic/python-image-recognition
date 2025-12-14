"""
Main application orchestrator.
Coordinates hand detection, gesture recognition, and visualization.
"""

import cv2
import time
import pyvirtualcam
from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.visualizer import Visualizer
from src.mouse_controller import MouseController
from src.drawing_manager import DrawingManager
from src.camera_stream import CameraStream
from src.ai_worker import AIWorker
from config.config import (
    CAMERA_INDEX, 
    MIRROR_VIEW, 
    WINDOW_NAME,
    ENABLE_MOUSE_CONTROL,
    DRAWING_MODE_KEY,
    CLEAR_SCREEN_KEY,
    VIRTUAL_CAMERA_ENABLED,
    DRAWING_COLOR_PINK,
    DRAWING_COLOR_BLUE,
    DRAWING_COLOR_GREEN
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
        
        # Async AI Data
        self.ai_worker = AIWorker(self.recognizer)
        
        self.visualizer = Visualizer()
        self.mouse_controller = MouseController() if enable_mouse_control else None
        self.drawing_manager = DrawingManager()
        self.cap = None
        self.enable_mouse_control = enable_mouse_control
        self.is_drawing_mode = False
        self.is_help_visible = True  # Show help on startup
        
        self.virtual_cam = None
        if VIRTUAL_CAMERA_ENABLED:
            try:
                # Initialize with a placeholder size, updated in run loop
                self.virtual_cam = pyvirtualcam.Camera(width=1280, height=720, fps=30)
                print(f"Virtual Camera started: {self.virtual_cam.device}")
            except Exception as e:
                print(f"Warning: Could not start Virtual Camera: {e}")
                self.virtual_cam = None
    
    def initialize_camera(self):
        """
        Initialize the camera and window.
        
        Returns:
            bool: True if camera opened successfully, False otherwise
        """
        # Use Threaded Camera Stream
        self.cap = CameraStream(src=CAMERA_INDEX).start()
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera at index {CAMERA_INDEX}")
            return False
            
        # Fullscreen Window Setup
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
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
        
        # Determine if we should process drawing or mouse actions
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
                
                action_result = 'none'

                if self.is_drawing_mode:
                    # Drawing Mode Logic
                    fingers = self.detector.fingersUp(hand_landmarks)
                    self.drawing_manager.update(frame, hand_landmarks, fingers)
                    
                    # Determine action description based on fingers
                    if fingers[1] and fingers[2]:
                        action_result = 'Selecting'
                    elif fingers[1] and not fingers[2]:
                        # Check pinch internal state from drawing manager would be cleaner, 
                        # but for UI text we can just say "Drawing/Hovering"
                        action_result = 'Drawing Mode'
                    else:
                        action_result = 'Hovering'
                else:
                    # Mouse Control Logic
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

        # Apply drawing overlay to frame
        frame = self.drawing_manager.get_overlay(frame)

        self.visualizer.draw_gesture_text(frame, gestures)
        
        # Draw UI Overlay (Status + Help)
        mode_str = "DRAWING" if self.is_drawing_mode else "MOUSE"
        self.visualizer.draw_ui_overlay(frame, mode_str, self.is_help_visible)
        
        return frame, gestures
    
    def run(self):
        """Main application loop."""

        if not self.initialize_camera():
            return
        
        # Start AI Brain
        self.ai_worker.start()
        
        self.visualizer.print_welcome_message()
        print(f"Press '{DRAWING_MODE_KEY}' to toggle Drawing Mode.")
        print(f"Press '{CLEAR_SCREEN_KEY}' to clear drawings.")
        
        try:
            while True:
                # 1. Capture (Instant)
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                    
                if MIRROR_VIEW:
                    frame = cv2.flip(frame, 1)
                
                # 2. To Brain (Non-blocking)
                self.ai_worker.submit_frame(frame.copy())
                
                # 3. Get Brain Results (Instant)
                _, gestures = self.ai_worker.get_results()
                
                # 4. Visual Engine
                # Draw Landmarks
                for gesture in gestures:
                    if 'landmarks' in gesture:
                        self.detector.draw_minimal_landmarks(frame, gesture['landmarks'])

                # Logic Loop
                current_action_desc = "NEUTRAL"
                
                for gesture in gestures:
                    hand_landmarks = gesture.get('landmarks')
                    action_result = gesture.get('action')
                    
                    if not hand_landmarks:
                        continue

                    # Mode Logic
                    if self.is_drawing_mode:
                        fingers = self.detector.fingersUp(hand_landmarks)
                        self.drawing_manager.update(frame, hand_landmarks, fingers)
                        if fingers[1] and fingers[2]: current_action_desc = 'Selecting'
                        elif fingers[1] and not fingers[2]: current_action_desc = 'Drawing Mode'
                        else: current_action_desc = 'Hovering'
                    else:
                        # Mouse Control
                        if self.enable_mouse_control and self.mouse_controller:
                            g_data = {'gesture_key': gesture['gesture'], 'action': gesture['action']}
                            status = self.mouse_controller.execute_action(g_data, hand_landmarks.landmark, frame.shape)
                            if status != 'No action':
                                current_action_desc = status
                                
                    gesture['action'] = current_action_desc
                
                # 5. Render Layers
                frame = self.drawing_manager.get_overlay(frame)
                self.visualizer.draw_gesture_text(frame, gestures)
                
                mode_str = "DRAWING" if self.is_drawing_mode else "MOUSE"
                self.visualizer.draw_ui_overlay(frame, mode_str, self.is_help_visible)

                # 6. Output
                if self.virtual_cam:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.virtual_cam.send(rgb_frame)
                    self.virtual_cam.sleep_until_next_frame()
                
                cv2.imshow(WINDOW_NAME, frame)
                
                # Input Handling
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'): return
                elif key == ord(DRAWING_MODE_KEY):
                    self.is_drawing_mode = not self.is_drawing_mode
                    print(f"Mode: {'Drawing' if self.is_drawing_mode else 'Mouse Control'}")
                elif key == ord(CLEAR_SCREEN_KEY):
                    self.drawing_manager.clear()
                    print("Canvas cleared")
                elif key == ord('h'): self.is_help_visible = not self.is_help_visible
                elif key == ord('1'): self.drawing_manager.set_color(DRAWING_COLOR_PINK)
                elif key == ord('2'): self.drawing_manager.set_color(DRAWING_COLOR_BLUE)
                elif key == ord('3'): self.drawing_manager.set_color(DRAWING_COLOR_GREEN)
                elif key == ord('0'): self.drawing_manager.set_eraser()

        finally:
            self.cleanup()
            self.ai_worker.stop()
        


    
    def cleanup(self):
        """Release resources and cleanup."""
        if self.cap:
            self.cap.stop()
        
        if self.virtual_cam:
            self.virtual_cam.close()
            
        cv2.destroyAllWindows()
        self.detector.close()
        self.visualizer.print_exit_message()
