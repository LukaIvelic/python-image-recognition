"""
Mouse controller module.
Handles PyAutoGUI actions based on detected gestures.
"""

import pyautogui
import time
import numpy as np
from src.one_euro_filter import OneEuroFilter
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
        # OneEuroFilter: min_cutoff=1.0 (stabilize slow), beta=0.007 (react fast)
        self.x_filter = OneEuroFilter(min_cutoff=0.1, beta=0.005, d_cutoff=1.0)
        self.y_filter = OneEuroFilter(min_cutoff=0.1, beta=0.005, d_cutoff=1.0)
        
        self.smoothing_factor = 0.5 # Deprecated but kept for compatibility logic loops if any
        
        # Action cooldowns to prevent spam
        self.last_click_time = 0
        self.last_scroll_time = 0
        self.click_cooldown = 0.5  # seconds
        self.scroll_cooldown = 0.2  # seconds
        
        # Current action tracking
        self.current_action = 'none'
        
    def smooth_position(self, x, y):
        """
        Apply smoothing to cursor position using OneEuroFilter.
        Adaptive: High smoothing when slow, Low latency when fast.
        """
        t = time.time()
        
        # Apply One Euro Filter
        screen_x = self.x_filter.filter(x, t)
        screen_y = self.y_filter.filter(y, t)
        
        return int(screen_x), int(screen_y)
    
    def hand_to_screen_coords(self, hand_x, hand_y, frame_width, frame_height):
        """
        Convert hand coordinates with robust mapping scaling.
        Ensures full screen reachability.
        """
        # Define the box within the camera view that maps to the full screen
        x_min = self.padding_x
        x_max = 1.0 - self.padding_x
        y_min = self.padding_y
        y_max = 1.0 - self.padding_y
        
        # Map x
        if hand_x < x_min: screen_x = 0
        elif hand_x > x_max: screen_x = self.screen_width
        else:
             screen_x = (hand_x - x_min) / (x_max - x_min) * self.screen_width
             
        # Map y
        if hand_y < y_min: screen_y = 0
        elif hand_y > y_max: screen_y = self.screen_height
        else:
            screen_y = (hand_y - y_min) / (y_max - y_min) * self.screen_height
        
        # MIRROR FIX: 
        # Config MIRROR_VIEW = True means camera frame is flipped.
        # So Hand Right -> Frame Right (x=1.0).
        # We want Cursor Right -> Screen Right (x=Width).
        # Current logic checks x=1.0 > x_max -> screen_x = Width.
        # This is CORRECT for mirroring.
        # No inversion lines should exist here.
        
        return int(screen_x), int(screen_y)
    
    def move_cursor(self, hand_x, hand_y, frame_width, frame_height):
        """
        Move the cursor based on hand position.
        """
        # MIRROR FIX: Use direct mapping. 
        # (Frame is already flipped if needed, so Left=Left, Right=Right)
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

