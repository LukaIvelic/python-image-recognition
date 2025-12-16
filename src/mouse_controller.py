"""
Mouse controller module.
Handles PyAutoGUI actions based on detected gestures.
"""

import pyautogui
import time
import numpy as np
from src.one_euro_filter import OneEuroFilter
from src.utils.geometry import GeometryUtils
from config.config import SCROLL_AMOUNT

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
        

        
        # Cursor smoothing
        self.prev_x = None
        self.prev_y = None
        self.curr_velocity = 0.0 # Velocity magnitude in pixels/frame
        # OneEuroFilter: min_cutoff=0.05 (High stabilization for slow movement), beta=0.005 (Responsiveness)
        # Reduced min_cutoff from 0.1 to 0.05 to fix "jittery cursor"
        self.x_filter = OneEuroFilter(min_cutoff=0.05, beta=0.005, d_cutoff=1.0)
        self.y_filter = OneEuroFilter(min_cutoff=0.05, beta=0.005, d_cutoff=1.0)
        
        
        # Scroll Filter (Smoother than cursor to prevent jittery scrolling)
        # beta=0.05 provides a good balance between lag and jitter suppression
        self.scroll_filter = OneEuroFilter(min_cutoff=0.5, beta=0.05, d_cutoff=1.0)
        
        self.smoothing_factor = 0.5 # Deprecated but kept for compatibility logic loops if any
        
        # Action cooldowns to prevent spam
        self.last_click_time = 0
        self.last_scroll_time = 0
        self.click_cooldown = 0.5  # seconds
        self.scroll_cooldown = 0.2  # seconds
        
        # Current action tracking
        self.current_action = 'none'
        self.is_dragging = False
        
        # Scroll Accumulator for Smooth Scrolling
        self.scroll_accumulator = 0.0
        
    def smooth_position(self, x, y):
        """
        Apply smoothing to cursor position using OneEuroFilter.
        Adaptive: High smoothing when slow, Low latency when fast.
        """
        t = time.time()
        
        # Apply One Euro Filter
        screen_x = self.x_filter.filter(x, t)
        screen_y = self.y_filter.filter(y, t)
        
        # Calculate Velocity (simple delta)
        if self.prev_x is not None and self.prev_y is not None:
             dx = screen_x - self.prev_x
             dy = screen_y - self.prev_y
             self.curr_velocity = (dx**2 + dy**2)**0.5
        else:
             self.curr_velocity = 0.0
             
        self.prev_x = screen_x
        self.prev_y = screen_y
        
        return int(screen_x), int(screen_y)
    

    
    def move_cursor(self, hand_x, hand_y, frame_width, frame_height):
        """
        Move the cursor based on hand position.
        """
        # Ensure we are NOT dragging when just moving
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False

        # MIRROR FIX: Use direct mapping. 
        # (Frame is already flipped if needed, so Left=Left, Right=Right)
        screen_x, screen_y = GeometryUtils.map_hand_to_screen(
            hand_x, hand_y, 
            self.screen_width, self.screen_height
        )
        
        # Apply smoothing
        smooth_x, smooth_y = self.smooth_position(screen_x, screen_y)
        
        # Move cursor
        try:
            pyautogui.moveTo(smooth_x, smooth_y, duration=0)
        except pyautogui.FailSafeException:
            pass

    def drag(self, hand_x, hand_y, frame_width, frame_height):
        """
        Drag cursor (Mouse Down + Move).
        """
        # Start Drag
        if not self.is_dragging:
            pyautogui.mouseDown()
            self.is_dragging = True
            
        # Convert absolute screen coords
        # Use Geometry Utils for mapping
        screen_x, screen_y = GeometryUtils.map_hand_to_screen(
            hand_x, hand_y, 
            self.screen_width, self.screen_height
        )
        
        # Apply smoothing
        smooth_x, smooth_y = self.smooth_position(screen_x, screen_y)
        
        # Move cursor
        try:
            pyautogui.moveTo(smooth_x, smooth_y, duration=0)
        except pyautogui.FailSafeException:
            pass

    
    def left_click(self):
        """Perform a left mouse click with cooldown."""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.click()
            print(">>> SINGLE LEFT CLICK EXECUTED")
            self.last_click_time = current_time
            return True
        return False
    
    def right_click(self):
        """Perform a right mouse click with cooldown."""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.rightClick()
            print(">>> RIGHT CLICK EXECUTED")
            self.last_click_time = current_time
            return True
        return False
    
    def double_click(self):
        """Perform a double click with cooldown."""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.doubleClick()
            print(">>> DOUBLE CLICK EXECUTED")
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

    def scroll_vertical(self, speed):
        """
        Scroll vertically based on speed.
        Uses accumulator for smooth sub-integer steps.
        
        Args:
            speed: Float, speed of scroll (positive=up, negative=down)
        """
        # Deadzone check
        if abs(speed) < 0.1:
            return False
            
        # Apply Smoothing
        t = time.time()
        smooth_speed = self.scroll_filter.filter(speed, t)
        
        # Add to accumulator
        self.scroll_accumulator += smooth_speed
        
        # Determine integer steps to take
        steps = int(self.scroll_accumulator)
        
        if steps != 0:
            pyautogui.scroll(steps)
            # Subtract steps from accumulator (keep fractional part)
            self.scroll_accumulator -= steps
            return True
            
        return False
    
    def execute_action(self, gesture_data, hand_landmarks, frame_shape):
        gesture_name = gesture_data.get('gesture_key', 'NEUTRAL')
        action = gesture_data.get('action', 'none')
        
        # Generic release check for actions that are NOT drag
        if action != 'drag' and self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False
        
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

        elif action == 'drag':
            self.drag(hand_x, hand_y, frame_width, frame_height)
            return 'Dragging'
        
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

    def get_velocity(self):
        """Return current cursor velocity magnitude."""
        return self.curr_velocity

