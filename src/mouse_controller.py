"""
Mouse controller module.
Handles PyAutoGUI actions based on detected gestures.
"""

import pyautogui
import time
import numpy as np
from config.config import HAND_PADDING_X, HAND_PADDING_Y, SCROLL_AMOUNT

# Configure PyAutoGUI
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.01  # Small pause between actions


class MouseController:
    """Controls mouse and keyboard using PyAutoGUI based on hand gestures."""
    
    def __init__(self, screen_width=None, screen_height=None):
        """
        Initialize the mouse controller.
        
        Args:
            screen_width: Screen width (auto-detected if None)
            screen_height: Screen height (auto-detected if None)
        """
        # Get screen dimensions
        if screen_width is None or screen_height is None:
            self.screen_width, self.screen_height = pyautogui.size()
        else:
            self.screen_width = screen_width
            self.screen_height = screen_height
        
        # Hand detection padding/margins
        # Use only the center portion of the camera view for mapping
        # This allows reaching screen edges while hand stays in detection zone
        self.padding_x = HAND_PADDING_X
        self.padding_y = HAND_PADDING_Y
        
        # Cursor smoothing
        self.prev_x = None
        self.prev_y = None
        self.smoothing_factor = 0.5  # 0 = no smoothing, 1 = max smoothing
        
        # Action cooldowns to prevent spam
        self.last_click_time = 0
        self.last_scroll_time = 0
        self.click_cooldown = 0.5  # seconds
        self.scroll_cooldown = 0.2  # seconds
        
        # Current action tracking
        self.current_action = 'none'
        
    def smooth_position(self, x, y):
        """
        Apply smoothing to cursor position for more stable movement.
        
        Args:
            x: New x coordinate
            y: New y coordinate
            
        Returns:
            tuple: (smoothed_x, smoothed_y)
        """
        if self.prev_x is None or self.prev_y is None:
            self.prev_x = x
            self.prev_y = y
            return x, y
        
        # Exponential moving average
        smooth_x = self.prev_x * self.smoothing_factor + x * (1 - self.smoothing_factor)
        smooth_y = self.prev_y * self.smoothing_factor + y * (1 - self.smoothing_factor)
        
        self.prev_x = smooth_x
        self.prev_y = smooth_y
        
        return int(smooth_x), int(smooth_y)
    
    def hand_to_screen_coords(self, hand_x, hand_y, frame_width, frame_height):
        """
        Convert hand coordinates (normalized 0-1) to screen coordinates with padding.
        
        The padding allows the hand to stay within the camera's detection zone
        while still being able to reach all screen edges.
        
        Args:
            hand_x: Normalized x coordinate from hand landmark (0-1)
            hand_y: Normalized y coordinate from hand landmark (0-1)
            frame_width: Width of the video frame
            frame_height: Height of the video frame
            
        Returns:
            tuple: (screen_x, screen_y)
        """
        # Apply padding: map the center portion of camera view to full screen
        # For example, with 15% padding: hand at 0.15-0.85 in camera maps to 0-1.0 on screen
        
        # Normalize with padding
        normalized_x = (hand_x - self.padding_x) / (1 - 2 * self.padding_x)
        normalized_y = (hand_y - self.padding_y) / (1 - 2 * self.padding_y)
        
        # Clamp to 0-1 range (allows going slightly outside the padded zone)
        normalized_x = max(0, min(1, normalized_x))
        normalized_y = max(0, min(1, normalized_y))
        
        # Map to screen coordinates (flip x for natural movement)
        screen_x = int((1 - normalized_x) * self.screen_width)
        screen_y = int(normalized_y * self.screen_height)
        
        # Final clamp to screen bounds
        screen_x = max(0, min(screen_x, self.screen_width - 1))
        screen_y = max(0, min(screen_y, self.screen_height - 1))
        
        return screen_x, screen_y
    
    def move_cursor(self, hand_x, hand_y, frame_width, frame_height):
        """
        Move the cursor based on hand position.
        
        Args:
            hand_x: Normalized x coordinate from hand landmark (0-1)
            hand_y: Normalized y coordinate from hand landmark (0-1)
            frame_width: Width of the video frame
            frame_height: Height of the video frame
        """
        screen_x, screen_y = self.hand_to_screen_coords(hand_x, hand_y, frame_width, frame_height)
        
        # Apply smoothing
        smooth_x, smooth_y = self.smooth_position(screen_x, screen_y)
        
        # Move cursor
        pyautogui.moveTo(smooth_x, smooth_y, duration=0)
    
    def left_click(self):
        """Perform a left mouse click with cooldown."""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.click()
            self.last_click_time = current_time
            return True
        return False
    
    def right_click(self):
        """Perform a right mouse click with cooldown."""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.rightClick()
            self.last_click_time = current_time
            return True
        return False
    
    def double_click(self):
        """Perform a double click with cooldown."""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.doubleClick()
            self.last_click_time = current_time
            return True
        return False
    
    def scroll_up(self, amount=None):
        """
        Scroll up.
        
        Args:
            amount: Scroll amount (positive = up), uses config default if None
        """
        if amount is None:
            amount = SCROLL_AMOUNT
            
        current_time = time.time()
        if current_time - self.last_scroll_time > self.scroll_cooldown:
            pyautogui.scroll(amount)
            self.last_scroll_time = current_time
            return True
        return False
    
    def scroll_down(self, amount=None):
        """
        Scroll down.
        
        Args:
            amount: Scroll amount (positive = down), uses config default if None
        """
        if amount is None:
            amount = SCROLL_AMOUNT
            
        current_time = time.time()
        if current_time - self.last_scroll_time > self.scroll_cooldown:
            pyautogui.scroll(-amount)
            self.last_scroll_time = current_time
            return True
        return False
    
    def execute_action(self, gesture_data, hand_landmarks, frame_shape):
        """
        Execute the appropriate action based on the detected gesture.
        
        Args:
            gesture_data: Dictionary with gesture information
            hand_landmarks: MediaPipe hand landmarks
            frame_shape: Tuple of (height, width, channels)
            
        Returns:
            str: Action performed
        """
        gesture_name = gesture_data.get('gesture_key', 'NEUTRAL')
        action = gesture_data.get('action', 'none')
        
        # Get index finger tip position for cursor control
        if hand_landmarks:
            index_tip = hand_landmarks[8]  # Index finger tip
            hand_x = index_tip.x
            hand_y = index_tip.y
            frame_height, frame_width = frame_shape[:2]
        else:
            hand_x = hand_y = 0.5
            frame_width = frame_height = 640
        
        # Execute action
        if action == 'move_cursor':
            self.move_cursor(hand_x, hand_y, frame_width, frame_height)
            return 'Moving cursor'
        
        elif action == 'left_click':
            if self.left_click():
                return 'Left click!'
            return 'Left click (cooldown)'
        
        elif action == 'right_click':
            if self.right_click():
                return 'Right click!'
            return 'Right click (cooldown)'
        
        elif action == 'double_click':
            if self.double_click():
                return 'Double click!'
            return 'Double click (cooldown)'
        
        elif action == 'scroll_up':
            if self.scroll_up():
                return 'Scrolling up'
            return 'Scroll up (cooldown)'
        
        elif action == 'scroll_down':
            if self.scroll_down():
                return 'Scrolling down'
            return 'Scroll down (cooldown)'
        
        elif action == 'stop':
            # Reset smoothing
            self.prev_x = None
            self.prev_y = None
            return 'Stopped'
        
        else:
            # No action or neutral
            return 'No action'

