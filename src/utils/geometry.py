"""
Geometry utility module.
Handles coordinate mapping and geometric calculations.
"""

import numpy as np
from config.config import HAND_PADDING_X, HAND_PADDING_Y

class GeometryUtils:
    """Static utilities for geometry and coordinate mapping."""
    
    @staticmethod
    def map_hand_to_screen(hand_x, hand_y, screen_width, screen_height):
        """
        Convert hand coordinates (0-1) to screen coordinates (pixels).
        Applies padding to allow reaching corners without over-extending.
        
        Args:
            hand_x: Normalized x coordinate (0.0 - 1.0)
            hand_y: Normalized y coordinate (0.0 - 1.0)
            screen_width: Width of the target screen in pixels
            screen_height: Height of the target screen in pixels
            
        Returns:
            tuple: (screen_x, screen_y) in pixels
        """
        # Remap coordinates to account for padding
        # This allows the user to reach the edges of the screen 
        # without moving their hand to the very edge of the camera view
        
        # X mapping
        x_min = HAND_PADDING_X
        x_max = 1.0 - HAND_PADDING_X
        x_mapped = (hand_x - x_min) / (x_max - x_min)
        
        # Y mapping
        y_min = HAND_PADDING_Y
        y_max = 1.0 - HAND_PADDING_Y
        y_mapped = (hand_y - y_min) / (y_max - y_min)
        
        # Clamp to 0-1
        x_mapped = np.clip(x_mapped, 0, 1)
        y_mapped = np.clip(y_mapped, 0, 1)
        
        # Convert to pixels
        screen_x = int(x_mapped * screen_width)
        screen_y = int(y_mapped * screen_height)
        
        return screen_x, screen_y
