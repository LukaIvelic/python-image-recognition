"""
Main application orchestrator.
Coordinates hand detection, gesture recognition, and visualization.
"""

import cv2
import time
import sys
import pyvirtualcam
from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.visualizer import Visualizer
from src.mouse_controller import MouseController
from src.drawing_manager import DrawingManager
from src.camera_stream import CameraStream
from src.ai_worker import AIWorker
import os
from contextlib import contextmanager
from collections import deque, Counter

@contextmanager
def suppress_stderr():
    """Suppress stderr to hide macOS system warnings."""
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        sys.stderr.flush()
        os.dup2(devnull, 2)
        yield
    except Exception:
        yield
    finally:
        try:
            os.dup2(old_stderr, 2)
            os.close(old_stderr)
            os.close(devnull)
        except:
            pass

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
    DRAWING_COLOR_GREEN,
    GESTURE_TRIGGER_DELAY,
    SCROLL_SPEED_MULTIPLIER, MOVEMENT_GRACE_PERIOD, GESTURE_TRIGGER_DELAY,
    GESTURE_TRIGGER_DELAY_CLICK, GESTURE_TRIGGER_DELAY_DOUBLE
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

        # Gesture Timing State
        self.last_gesture_name = None
        self.gesture_start_time = 0
        self.scroll_zero_y = None # Zero point for joystick scrolling
        self.last_scroll_active_time = 0 # Timer for sticky scroll
        self.last_scroll_active_time = 0 # Timer for sticky scroll
        self.last_scroll_active_time = 0 # Timer for sticky scroll
        self.gesture_buffer = deque(maxlen=6) # Increased buffer for stability (prevents flicker)
        self.hand_visible_start_time = 0 # Timer for hand entry debounce
        self.last_movement_time = 0 # Timer for movement debounce (Pinch -> Click transition)
        self.gesture_triggered = False # Flag for single-shot actions
        self.needs_reset = False # Flag to force neutral state between clicks
        self.hand_visible_start_time = 0 # Timer for hand entry debounce
        self.gesture_triggered = False # Flag for single-shot actions
    
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
            
        # Normal Window Setup (resizable with title bar)
        # Suppress macOS Secure Coding warning
        with suppress_stderr():
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        
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
                # --- HAND ENTRY DEBOUNCE LOGIC ---
                if self.hand_visible_start_time == 0:
                    self.hand_visible_start_time = time.time()
                
                # If hand has been visible for less than 0.8 seconds, stabilize only
                is_stabilizing = (time.time() - self.hand_visible_start_time) < 0.8
                
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
                        
                        # Check Debounce
                        if is_stabilizing:
                            action_result = "Stabilizing..."
                        else:
                            # --- TRIGGER DELAY LOGIC ---
                            current_gesture = gesture_info['gesture_key']
                            
                            # "Move Cursor" (Pinch) and "Drag" (Fist) are instant movement
                            if current_gesture in ['CURSOR_CONTROL', 'DRAG']:
                                 action_result = self.mouse_controller.execute_action(
                                    gesture_info,
                                    hand_landmarks.landmark,
                                    frame.shape
                                )
                                 # Reset timer if we switch to move
                                 self.last_gesture_name = current_gesture

                            # "SCROLL ACTIVE" (Joystick Mode)
                            elif current_gesture == 'SCROLL_ACTIVE':
                                 if self.last_gesture_name != 'SCROLL_ACTIVE' or self.scroll_zero_y is None:
                                     self.scroll_zero_y = hand_landmarks.landmark[8].y
                                 
                                 dy = hand_landmarks.landmark[8].y - self.scroll_zero_y
                                 speed = -dy * SCROLL_SPEED_MULTIPLIER
                                 
                                 self.mouse_controller.scroll_vertical(speed)
                                 
                                 # Determine status text with direction
                                 direction = "NEUTRAL"
                                 if speed > 0.5: direction = "UP"
                                 elif speed < -0.5: direction = "DOWN"
                                 
                                 action_result = f"Scrolling {direction} ({abs(speed):.1f})"
                                 
                                 # Keep last gesture name updated to avoid re-triggering delays if we switch back
                                 self.last_gesture_name = 'SCROLL_ACTIVE'
                            
                            # "Stop" are instant status updates
                            elif current_gesture == 'STOP':
                                 action_result = self.mouse_controller.execute_action(
                                    gesture_info,
                                    hand_landmarks.landmark,
                                    frame.shape
                                )
                                 self.last_gesture_name = current_gesture
                                
                            # CLICKS require Delay
                            else:
                                    if current_gesture == self.last_gesture_name:
                                        # Holding the same gesture
                                        if time.time() - self.gesture_start_time > GESTURE_TRIGGER_DELAY:
                                            # Threshold passed
                                            
                                            # For Clicks, we only trigger ONCE per gesture instance (Single-Shot)
                                            if not self.gesture_triggered:
                                                action_result = self.mouse_controller.execute_action(
                                                    gesture_info, # Changed from g_data to gesture_info to match original code's variable
                                                    hand_landmarks.landmark,
                                                    frame.shape
                                                )
                                                self.gesture_triggered = True
                                            else:
                                                action_result = "Action Complete (Release to reset)"
                                        else:
                                            # Waiting...
                                            remaining = GESTURE_TRIGGER_DELAY - (time.time() - self.gesture_start_time)
                                            action_result = f"Hold... {remaining:.1f}s"
                                    else:
                                        # New gesture started
                                        self.last_gesture_name = current_gesture
                                        self.gesture_start_time = time.time()
                                        self.scroll_zero_y = None # Reset scroll zero
                                        self.gesture_triggered = False # Reset trigger for new gesture
                                        action_result = "Hold to trigger..."
                
                gestures.append({
                    'hand': hand_label,
                    'gesture': gesture_info['name'], # Display Name
                    'gesture_key': gesture_info['gesture_key'], # Raw Key for logic
                    'action': action_result,
                    'confidence': confidence
                })
        else:
            # No hands detected - Reset Debounce Timer
            self.hand_visible_start_time = 0

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
                            # --- STABILITY / HYSTERESIS ---
                            # Use KEY for smoothing, not display name
                            raw_key = gesture.get('gesture_key', 'UNKNOWN')
                            
                            # VELOCITY LOCK: If moving fast, lock to previous movement gesture
                            # This prevents "Flickering" to Neutral/IndexUp during fast swipes
                            velocity = self.mouse_controller.get_velocity()
                            if velocity > 50.0: # High speed threshold (px/frame)
                                # If we were moving cursor or dragging, KEEP DOING IT
                                if self.last_gesture_name in ['CURSOR_CONTROL', 'DRAG']:
                                    raw_key = self.last_gesture_name
                                    # Override action too?
                                    # We need to ensure the action is consistent.
                                    # If locking to DRAG, action is 'drag'.
                                    # If locking to CURSOR_CONTROL, action is 'move_cursor'.
                                    # The buffer logic below will handle stability, but we force the INPUT to the buffer.
                            
                            self.gesture_buffer.append(raw_key)
                            
                            target_key = raw_key
                            target_action = gesture['action']
                            
                            # Find most common gesture in buffer (Mode)
                            is_stable = False # Track if the current target_key is stable
                            if len(self.gesture_buffer) > 0:
                                # Priority: If SCROLL_ACTIVE is in buffer at all, assume it's intent
                                # Because it's a hard pose to hold perfectly stable
                                if 'SCROLL_ACTIVE' in self.gesture_buffer:
                                    target_key = 'SCROLL_ACTIVE'
                                    is_stable = True # Scroll is prioritized
                                else:
                                    counter = Counter(self.gesture_buffer)
                                    stable_key, count = counter.most_common(1)[0]
                                    
                                    stability_threshold = 4 # Strict majority (4/6)
                                    if count >= stability_threshold:
                                        target_key = stable_key
                                        is_stable = True
                                
                                # If we are overriding the gesture, we need to fetch the correct Action
                                if target_key != raw_key:
                                    # Special case: SCROLL_ACTIVE isn't in standard GESTURES dict sometimes?
                                    # It IS in GESTURES? No, it's dynamic in recognizer.
                                    # Recognizer returns 'action': 'scroll_active'.
                                    # If target_key is SCROLL_ACTIVE, action is scroll_active.
                                    # If target_key is in self.recognizer.gestures:
                                    if target_key in self.recognizer.gestures:
                                        target_action = self.recognizer.gestures[target_key]['action']
                                    elif target_key == 'SCROLL_ACTIVE':
                                        target_action = 'scroll_active'
                                    elif target_key == 'CURSOR_CONTROL': # Pinch
                                        target_action = 'move_cursor'
                            
                            # FIX: We need the GESTURE KEY (e.g. 'DRAG'), not the display name.
                            # `gesture` dict from process_frame/AIWorker needs to carry 'gesture_key'.
                            
                            g_data = {'gesture_key': target_key, 'action': target_action}
                            
                            # --- SCROLL LATCHING LOGIC ---
                            # Check if we should override the detected gesture with "SCROLL_ACTIVE" due to grace period
                            is_scrolling = (target_key == 'SCROLL_ACTIVE')
                            
                            if is_scrolling:
                                self.last_scroll_active_time = time.time()
                            
                            # If not currently scrolling, but within grace period, FORCE scroll
                            if not is_scrolling and self.scroll_zero_y is not None:
                                if (time.time() - self.last_scroll_active_time) < 0.5: # 0.5s Grace Period
                                    is_scrolling = True
                                    target_key = 'SCROLL_ACTIVE'
                                    target_action = 'scroll_active'
                                    is_stable = True # Forced scroll is stable
                                    # Update g_data to reflect forced scroll
                                    g_data = {'gesture_key': target_key, 'action': target_action}

                            # Execute Action
                            if is_scrolling:
                                 # Joystick Logic
                                 # Initialize Zero Point if needed
                                 if self.scroll_zero_y is None:
                                     self.scroll_zero_y = hand_landmarks.landmark[8].y
                                 
                                 # Calculate Speed based on distance from Zero Point
                                 current_y = hand_landmarks.landmark[8].y
                                 dy = current_y - self.scroll_zero_y
                                 speed = -dy * SCROLL_SPEED_MULTIPLIER
                                 
                                 self.mouse_controller.scroll_vertical(speed)
                                 
                                 # Determine status text with direction
                                 direction = "NEUTRAL"
                                 if speed > 0.5: direction = "UP"
                                 elif speed < -0.5: direction = "DOWN"
                                 
                                 action_result = f"Scrolling {direction} ({abs(speed):.1f})"
                                 
                                 # Keep last gesture name updated to avoid re-triggering delays if we switch back
                                 self.last_gesture_name = 'SCROLL_ACTIVE'
                            
                            else:
                                # Not scrolling
                                self.scroll_zero_y = None # Reset Zero Point
                                
                                # Separate Instant vs Delayed Actions
                                is_click_action = target_key in ['LEFT_CLICK', 'RIGHT_CLICK', 'DOUBLE_CLICK']
                                
                                # NEUTRAL RESET CHECK
                                if self.needs_reset:
                                    # Strictly require a STABLE non-click gesture to reset
                                    if not is_click_action and is_stable:
                                        self.needs_reset = False
                                    else:
                                        action_result = "Release to Reset"
                                        continue 
                                
                                if not is_click_action:
                                    # Instant Execution (Move, Drag, Stop, etc.)
                                    status = self.mouse_controller.execute_action(g_data, hand_landmarks.landmark, frame.shape)
                                    if status != 'No action':
                                        action_result = status
                                        
                                    # Update state for continuous actions
                                    self.last_gesture_name = target_key
                                    self.gesture_start_time = time.time()
                                    self.gesture_triggered = False
                                    
                                    # Update movement time if we were moving
                                    if target_key in ['CURSOR_CONTROL', 'DRAG']:
                                        self.last_movement_time = time.time()

                                else:
                                    # Delayed Execution (Clicks)
                                    # Logic for Trigger Delays
                                     if target_key == self.last_gesture_name:
                                        # Check Debounce from Movement
                                        if (time.time() - self.last_movement_time) < MOVEMENT_GRACE_PERIOD:
                                              action_result = "Stabilizing..."
                                              # Keep resetting start time so we don't trigger immediately after grace period ends
                                              self.gesture_start_time = time.time() 
                                        
                                        else:
                                            # Determine Trigger Delay based on gesture
                                            trigger_delay = GESTURE_TRIGGER_DELAY_CLICK
                                            if target_key == 'DOUBLE_CLICK':
                                                trigger_delay = GESTURE_TRIGGER_DELAY_DOUBLE
                                            
                                            if time.time() - self.gesture_start_time > trigger_delay:
                                                # Single Shot Logic
                                                if not self.gesture_triggered:
                                                    # NOW we execute the action!
                                                    status = self.mouse_controller.execute_action(g_data, hand_landmarks.landmark, frame.shape)
                                                    action_result = status
                                                    self.gesture_triggered = True
                                                    self.needs_reset = True # Force reset after click
                                                else:
                                                     action_result = "Action Complete"
                                            else:
                                                remaining = trigger_delay - (time.time() - self.gesture_start_time)
                                                action_result = f"Hold... {remaining:.1f}s"
                                     else:
                                         # Start Timer
                                         self.last_gesture_name = target_key
                                         self.gesture_start_time = time.time()
                                         self.gesture_triggered = False
                                         action_result = "Hold to trigger..."
                                         

                
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
