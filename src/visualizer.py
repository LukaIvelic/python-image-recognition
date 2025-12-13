"""
Visualization module.
Handles all display and drawing operations for the application.
"""

import cv2
from config.config import (
    FONT,
    FONT_SCALE,
    FONT_COLOR,
    FONT_THICKNESS,
    TEXT_Y_OFFSET,
    TEXT_LINE_HEIGHT,
    TERMINAL_WIDTH,
    SEPARATOR_CHAR
)
from config.gestures import get_gesture_list


class Visualizer:
    """Handles visualization and terminal output."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.previous_gestures = []
    
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
    
    def print_welcome_message(self):
        """Print welcome message and instructions to terminal."""
        separator = SEPARATOR_CHAR * TERMINAL_WIDTH
        
        print(separator)
        print("Hand Gesture Recognition System")
        print(separator)
        print("\nRecognizable Gestures:")
        
        gesture_list = get_gesture_list()
        for gesture in gesture_list:
            print(gesture)
        
        print("\nPress 'q' to quit")
        print(separator)
        print()
    
    def print_gestures(self, gestures):
        """
        Print detected gestures to terminal.
        Only prints when gestures change.
        
        Args:
            gestures: List of detected gesture dictionaries
        """
        
        if gestures != self.previous_gestures:
            # Terminal printing commented out
            # separator = SEPARATOR_CHAR * TERMINAL_WIDTH
            # 
            # if gestures:
            #     print("\n" + separator)
            #     for gesture_data in gestures:
            #         hand = gesture_data['hand']
            #         gesture = gesture_data['gesture']
            #         action = gesture_data.get('action', '')
            #         confidence = gesture_data['confidence']
            #         
            #         print(f"Hand: {hand:5} | "
            #               f"Gesture: {gesture:20} | "
            #               f"Action: {action:25} | "
            #               f"Confidence: {confidence:.2f}")
            #     print(separator)
            # else:
            #     print("\nNo hands detected")
            
            self.previous_gestures = gestures.copy()
    
    def print_exit_message(self):
        """Print exit message."""
        print("\nGesture recognition stopped.")

