"""
Visualization module.
Handles all display and drawing operations for the application.
"""

import cv2
import numpy as np
from config.config import (
    FONT,
    FONT_SCALE,
    FONT_COLOR,
    FONT_THICKNESS,
    TEXT_Y_OFFSET,
    TEXT_LINE_HEIGHT,
    TERMINAL_WIDTH
)
from config.gestures import get_gesture_list
from src.ui.hud import HUD


class Visualizer:
    """Handles visualization and terminal output."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.previous_gestures = []
        
        # Initialize UI HUD
        self.hud = HUD()
        self.last_mode = None
        self.last_help_visible = None
    
    def draw_gesture_text(self, frame, gestures):
        """
        Draw gesture text on the video frame.
        
        Args:
            frame: Image to draw on
            gestures: List of detected gesture dictionaries
        """
        for i, gesture_data in enumerate(gestures):
            hand = gesture_data['hand']
            gesture = gesture_data['gesture']
            action = gesture_data.get('action', '')
            
            # Primary text: hand and gesture
            text = f"{hand}: {gesture}"
            y_position = TEXT_Y_OFFSET + i * TEXT_LINE_HEIGHT
            
            cv2.putText(
                frame,
                text,
                (10, y_position),
                FONT,
                FONT_SCALE,
                FONT_COLOR,
                FONT_THICKNESS
            )
            
            # Secondary text: action (if any)
            if action and action != 'none' and action != 'No action':
                action_text = f"  -> {action}"
                cv2.putText(
                    frame,
                    action_text,
                    (10, y_position + 25),
                    FONT,
                    0.6,
                    (255, 255, 0),  # Cyan color for actions
                    1
                )
    
    def draw_ui_overlay(self, frame, mode, is_help_visible):
        """
        Draw UI overlay using the HUD module.
        """
        return self.hud.draw_ui_overlay(frame, mode, is_help_visible)

    def print_welcome_message(self):
        """Print the welcome message to the terminal."""
        print("=" * TERMINAL_WIDTH)
        print("Hand Gesture Recognition System".center(TERMINAL_WIDTH))
        print("=" * TERMINAL_WIDTH)
        print("\nRecognizable Gestures:")
        
        gestures = get_gesture_list()
        for gesture_line in gestures:
            print(gesture_line)
            
        print(f"\nPress 'q' to quit")
        print("=" * TERMINAL_WIDTH + "\n")
        print()
    
    def print_gestures(self, gestures):
        """
        Print detected gestures to terminal.
        Only prints when gestures change.
        
        Args:
            gestures: List of detected gesture dictionaries
        """
        
        if gestures != self.previous_gestures:
             self.previous_gestures = gestures.copy()
    
    def print_exit_message(self):
        """Print exit message."""
        print("\nGesture recognition stopped.")
