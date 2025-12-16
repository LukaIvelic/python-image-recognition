"""
HUD / UI Overlay module.
Handles the "Glass" style UI and text rendering.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import platform

from config.config import (
    FONT_COLOR, FONT_SCALE, FONT_THICKNESS, 
    WINDOW_NAME, HEADER_HEIGHT
)

class HUD:
    """Heads-Up Display for the application."""
    
    def __init__(self):
        """Initialize the HUD resources."""
        # Cache for UI Overlay
        self.ui_cache = None
        
    def draw_ui_overlay(self, frame, mode, is_help_visible):
        """
        Draw UI overlay with Modern "Glass" style and HD Text.
        Uses caching to avoid expensive PIL operations every frame.
        """
        h, w, c = frame.shape
        
        # Create or update cache if dimensions change
        if self.ui_cache is None or self.ui_cache.shape != frame.shape:
             self.ui_cache = np.zeros((h, w, c), dtype=np.uint8)
             
             # --- 1. Draw Static Elements (Backgrounds) on Cache ---
             # Header Background (Glass Effect)
             cv2.rectangle(self.ui_cache, (0, 0), (w, HEADER_HEIGHT), (20, 20, 20), cv2.FILLED)
             
             # Title
             self.ui_cache = self._draw_text_pil(
                 self.ui_cache, 
                 "AI HAND CONTROL", 
                 (30, 30), 
                 font_size=28, 
                 color=(255, 255, 255)
             )
             
             # Subtitle / Instructions
             self.ui_cache = self._draw_text_pil(
                 self.ui_cache, 
                 "Press 'd' to Draw  |  'q' to Quit", 
                 (30, 75), 
                 font_size=16, 
                 color=(180, 180, 180)
             )

        # --- Dynamic Frame Composition ---
        
        # 1. Blend Frame with Cached Static UI
        # We want the UI background to be semi-transparent "Glass"
        # Extract UI region
        ui_roi = self.ui_cache[0:HEADER_HEIGHT, 0:w]
        frame_roi = frame[0:HEADER_HEIGHT, 0:w]
        
        # Create mask where we have drawn text/shapes
        # Simple grayscale threshold
        gray_ui = cv2.cvtColor(ui_roi, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_ui, 1, 255, cv2.THRESH_BINARY)
        
        # Darken the background area slightly (Glass tint)
        glass_roi = cv2.addWeighted(frame_roi, 0.7, ui_roi, 0.3, 0)
        
        # Copy the glass tint back
        frame[0:HEADER_HEIGHT, 0:w] = glass_roi
        
        # 2. Draw Dynamic Status Text (Mode)
        status_color = (0, 255, 0) if mode == "MOUSE" else (255, 0, 255) # Green vs Pink
        
        # Right aligned mode text
        mode_text = f"MODE: {mode}"
        
        # Since PIL drawing is slow, we use cv2 for dynamic per-frame text 
        # OR we just accept the slight hit for quality. 
        # Let's use PIL for quality but optimized.
        
        # Actually, let's overlay the cached *white* text on top of the glass
        # (Where mask is > 0, copy pixel from cache to frame)
        frame_roi_bg = frame[0:HEADER_HEIGHT, 0:w]
        frame_roi_bg[mask > 0] = ui_roi[mask > 0]
        
        # Now draw dynamic Mode text
        # Using OpenCV for dynamic text is 100x faster than PIL conversion loop
        cv2.putText(
            frame, 
            mode_text, 
            (w - 250, 60), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.0, 
            status_color, 
            2, 
            cv2.LINE_AA
        )
        
        if is_help_visible:
            # Draw Help Overlay... (Simplified for now)
            pass
            
        return frame

    def _draw_text_pil(self, img, text, pos, font_size=20, color=(255, 255, 255)):
        """
        Draw text using PIL for High Definition quality.
        """
        # Convert to PIL
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # Load font (Platform specific)
        try:
            if platform.system() == "Darwin": # macOS
                font = ImageFont.truetype("Arial.ttf", font_size)
            elif platform.system() == "Windows":
                 font = ImageFont.truetype("arial.ttf", font_size)
            else:
                 font = ImageFont.load_default()
        except IOError:
            font = ImageFont.load_default()
        
        # Draw text
        draw.text(pos, text, font=font, fill=color)
        
        # Convert back to OpenCV
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
