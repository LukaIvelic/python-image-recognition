"""
Visualization module.
Handles all display and drawing operations for the application.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont # PIL for HD Text
import platform

from config.config import (
    FONT,
    FONT_SCALE,
    FONT_COLOR,
    FONT_THICKNESS,
    TEXT_Y_OFFSET,
    TEXT_LINE_HEIGHT,
    TERMINAL_WIDTH,
    SEPARATOR_CHAR,
    WINDOW_NAME,
    DRAWING_COLOR_PINK,
    DRAWING_COLOR_BLUE,
    DRAWING_COLOR_GREEN
)
from config.gestures import get_gesture_list


class Visualizer:
    """Handles visualization and terminal output."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.previous_gestures = []
        
        # Cache for UI Overlay
        self.ui_cache = None
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
        Draw UI overlay with Modern "Glass" style and HD Text.
        Uses caching to avoid expensive PIL operations every frame.
        
        Args:
            frame: Image to draw on
            mode: Current mode string (e.g., "MOUSE", "DRAWING")
            is_help_visible: Boolean to show help menu
        """
        h, w, c = frame.shape
        
        # Check cache validity
        cache_valid = (
            self.ui_cache is not None and 
            self.ui_cache.size == (w, h) and # Check size as well
            self.last_mode == mode and
            self.last_help_visible == is_help_visible
        )
        
        if not cache_valid:
            # Recreate Cache
            try:
                # Initialize Cache Canvas (RGBA)
                self.ui_cache = Image.new('RGBA', (w, h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(self.ui_cache)
                
                # ... Load Fonts ...
                try:
                    if platform.system() == "Darwin":
                        font_bold = ImageFont.truetype("SFNS.ttf", 30)
                        font_norm = ImageFont.truetype("SFNS.ttf", 20)
                        font_small = ImageFont.truetype("SFNS.ttf", 16)
                    else:
                        font_bold = ImageFont.truetype("arialbd.ttf", 30)
                        font_norm = ImageFont.truetype("arial.ttf", 20)
                        font_small = ImageFont.truetype("arial.ttf", 16)
                except IOError:
                    font_bold = ImageFont.load_default()
                    font_norm = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                
                # --- 1. Badge Text ---
                badge_text = f"MODE: {mode}"
                bbox = draw.textbbox((0, 0), badge_text, font=font_norm)
                fw, fh = bbox[2] - bbox[0], bbox[3] - bbox[1]
                
                text_color = (0, 255, 255) if mode == "MOUSE" else (255, 0, 255)
                draw.text((w // 2 - fw // 2, 35), badge_text, font=font_norm, fill=text_color)
                
                # Hint
                draw.text((w - 200, h - 30), "Press 'h' for Help", font=font_small, fill=(200, 200, 200))
                
                # --- 2. Help Menu Text ---
                if is_help_visible:
                     box_w, box_h = 600, 450
                     x1, y1 = (w - box_w) // 2, (h - box_h) // 2
                     
                     # Title
                     draw.text((x1 + 40, y1 + 40), "HAND GESTURE GUIDE", font=font_bold, fill=(255, 255, 255))
                     
                     col1_x = x1 + 40
                     col2_x = x1 + 320
                     start_y = y1 + 100
                     step = 50
                     
                     # Gestures
                     draw.text((col1_x, start_y), "GESTURES", font=font_norm, fill=(0, 255, 255))
                     gestures_list = [
                         ("Index Point", "Move Cursor"),
                         ("Pinch (Index+Thumb)", "Draw"),
                         ("Index Up", "Hover"),
                         ("Fist", "Pause")
                     ]
                     for i, (g, desc) in enumerate(gestures_list):
                         y = start_y + 40 + (i * step)
                         draw.text((col1_x, y), g, font=font_norm, fill=(220, 220, 220))
                         draw.text((col1_x, y + 22), desc, font=font_small, fill=(150, 150, 150))
                         
                     # Controls
                     draw.text((col2_x, start_y), "CONTROLS", font=font_norm, fill=(0, 255, 255))
                     controls = [
                         ("'d'", "Toggle Draw/Mouse"),
                         ("'c'", "Clear Canvas"),
                         ("'h'", "Toggle Help"),
                         ("'q'", "Quit App"),
                         ("1/2/3", "Colors"),
                         ("0", "Eraser")
                     ]
                     for i, (k, desc) in enumerate(controls):
                         y = start_y + 40 + (i * step)
                         draw.text((col2_x, y), k, font=font_norm, fill=(255, 255, 0))
                         draw.text((col2_x + 60, y), desc, font=font_small, fill=(200, 200, 200))

                # Update State
                self.last_mode = mode
                self.last_help_visible = is_help_visible
                
            except Exception as e:
                print(f"UI Cache Error: {e}")
                self.ui_cache = None

        # --- DRAWING (Every Frame) ---
        # 1. Draw Dynamic Shapes (Glass Boxes) using OpenCV (Fast)
        # Badge Box
        # Simplified box dimensions for the overlay rectangle
        bx1, by1 = w // 2 - 100, 20
        bx2, by2 = w // 2 + 100, 70
        
        # Pill Overlay
        # Ensure coordinates are within frame bounds
        bx1 = max(0, bx1)
        by1 = max(0, by1)
        bx2 = min(w, bx2)
        by2 = min(h, by2)

        if bx2 > bx1 and by2 > by1: # Check if valid region
            sub = frame[by1:by2, bx1:bx2]
            res = cv2.addWeighted(sub, 0.4, np.zeros(sub.shape, sub.dtype), 0.6, 0) # Darken
            frame[by1:by2, bx1:bx2] = res
            cv2.rectangle(frame, (bx1, by1), (bx2, by2), (100, 100, 100), 1)
        
        if is_help_visible:
             box_w, box_h = 600, 450
             x1, y1 = (w - box_w) // 2, (h - box_h) // 2
             x2, y2 = x1 + box_w, y1 + box_h
             
             # Full Dim
             cv2.addWeighted(frame, 0.7, np.zeros(frame.shape, frame.dtype), 0.3, 0, frame)
             
             # Menu Box
             # Ensure coordinates are within frame bounds
             x1 = max(0, x1)
             y1 = max(0, y1)
             x2 = min(w, x2)
             y2 = min(h, y2)

             if x2 > x1 and y2 > y1: # Check if valid region
                sub = frame[y1:y2, x1:x2]
                res = cv2.addWeighted(sub, 0.2, np.zeros(sub.shape, sub.dtype), 0.8, 0) # Very Dark
                frame[y1:y2, x1:x2] = res
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)

        # 2. Blend Cached PIL Text Layer
        if self.ui_cache:
            # Convert PIL RGBA to OpenCV
            overlay_rgba = np.array(self.ui_cache)
            
            # Split into BGR and Alpha channels
            b, g, r, a = cv2.split(overlay_rgba)
            overlay_bgr = cv2.merge([b, g, r])
            
            # Create a 3-channel alpha mask
            alpha_mask = a / 255.0
            alpha_mask_3_channel = cv2.merge([alpha_mask, alpha_mask, alpha_mask])

            # Blend the overlay onto the frame
            frame[:] = (frame * (1 - alpha_mask_3_channel) + overlay_bgr * alpha_mask_3_channel).astype(np.uint8)

    
    def _draw_text_pil(self, img, text, pos, font_size=20, color=(255, 255, 255)):
        """
        Draw text using PIL for High Definition quality.
        args:
            img: OpenCV image (BGR)
            text: String to draw
            pos: (x, y) tuple
            font_size: Size of font
            color: (R, G, B) tuple
        returns:
            OpenCV image (BGR) with text
        """
        # Convert BGR to RGB
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # Load Font (Try system fonts)
        try:
            # Mac default
            if platform.system() == "Darwin":
                font = ImageFont.truetype("SFNS.ttf", font_size) # San Francisco
            else:
                font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # Fallback to default
            font = ImageFont.load_default()
            
        draw.text(pos, text, font=font, fill=color)
        
        # Convert back to BGR
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
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

