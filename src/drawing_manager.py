"""
Drawing Manager module.
Handles drawing operations on a separate canvas layer.
"""

import cv2
import numpy as np
from config.config import (
    DRAWING_THICKNESS,
    ERASER_THICKNESS
)


import cv2
import numpy as np
import math
from config.config import (
    HEADER_HEIGHT,
    DRAWING_COLOR_PINK,
    DRAWING_COLOR_BLUE,
    DRAWING_COLOR_GREEN,
    ERASER_COLOR,
    DEFAULT_DRAWING_COLOR,
    DRAWING_THICKNESS,
    ERASER_THICKNESS,
    SMOOTHING_FACTOR,
    DRAWING_OPACITY
)


class DrawingManager:
    """Manages drawing state, canvas, and UI header."""

    def __init__(self):
        """Initialize the drawing manager."""
        self.canvas = None
        
        # Drawing State
        self.draw_color = DEFAULT_DRAWING_COLOR
        self.brush_thickness = DRAWING_THICKNESS
        
        # Smoothing
        self.xp, self.yp = 0, 0
        
        # Header UI
        self.header_img = None
    
    def _initialize_canvas(self, frame_shape):
        """Initialize canvas if it doesn't exist or shape changed."""
        if self.canvas is None or self.canvas.shape != frame_shape:
            self.canvas = np.zeros(frame_shape, dtype=np.uint8)
            
    def _create_header(self, width):
        """Create the header UI image."""
        header = np.zeros((HEADER_HEIGHT, width, 3), np.uint8)
        
        # Define regions
        # Pink | Blue | Eraser
        section_width = width // 3
        
        # Pink
        cv2.rectangle(header, (0, 0), (section_width, HEADER_HEIGHT), DRAWING_COLOR_PINK, cv2.FILLED)
        cv2.putText(header, "PINK", (section_width//2 - 50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Blue
        cv2.rectangle(header, (section_width, 0), (2 * section_width, HEADER_HEIGHT), DRAWING_COLOR_BLUE, cv2.FILLED)
        cv2.putText(header, "BLUE", (int(1.5 * section_width) - 50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Eraser
        cv2.rectangle(header, (2 * section_width, 0), (width, HEADER_HEIGHT), (200, 200, 200), cv2.FILLED)
        cv2.putText(header, "ERASER", (int(2.5 * section_width) - 60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        return header

    def clear_canvas(self):
        """Clear the drawing canvas."""
        if self.canvas is not None:
            self.canvas.fill(0)
            self.xp, self.yp = 0, 0

    def update(self, frame, hand_landmarks, fingers):
        """
        Update drawing state based on hand position and gesture.
        
        Args:
            frame: Current video frame
            hand_landmarks: MediaPipe hand landmarks
            fingers: List of booleans [Thumb, Index, Middle, Ring, Pinky]
        """
        self._initialize_canvas(frame.shape)
        h, w, c = frame.shape
        
        # Header Removed per User Request (Keyboard Control Only)

        if not hand_landmarks:
            self.xp, self.yp = 0, 0
            return

        # Get coordinates
        # Index Tip (8)
        x1, y1 = int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)
        
        # --- DRAWING MODE ---
        # Implement "Pinch to Draw" (Index + Thumb are close)
        # We need distance between Index Tip (8) and Thumb Tip (4)
        x_thumb, y_thumb = int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h)
        
        # Calculate distance
        length = math.hypot(x1 - x_thumb, y1 - y_thumb)
        
        # Threshold for pinch (tune this)
        pinch_threshold = 60 # Increased to make extended pinch easier
        
        is_pinching = length < pinch_threshold
        
        # Midpoint Calculation
        # Use midpoint between Thumb and Index for drawing
        cx = (x1 + x_thumb) // 2
        cy = (y1 + y_thumb) // 2
        
        # Drawing Logic
        # Condition: Pinching AND Middle Finger Down.
        # (We ignore fingers[1]/Index up/down because pinching usually curls the index finger)
        if is_pinching and not fingers[2]:
            # Draw point at Midpoint
            cv2.circle(frame, (cx, cy), 15, self.draw_color, cv2.FILLED)
            
            if self.xp == 0 and self.yp == 0:
                self.xp, self.yp = cx, cy
                
            # Improved Smoothing (Elastic/Lag)
            smooth_x = int(self.xp + (cx - self.xp) * SMOOTHING_FACTOR)
            smooth_y = int(self.yp + (cy - self.yp) * SMOOTHING_FACTOR)
            
            # Draw line on canvas
            cv2.line(self.canvas, (self.xp, self.yp), (smooth_x, smooth_y), self.draw_color, self.brush_thickness)
            
            self.xp, self.yp = smooth_x, smooth_y
            
        else:
            self.xp, self.yp = 0, 0

    def get_overlay(self, frame):
        """
        Overlay the drawing canvas onto the frame.
        Optimized for performance while keeping translucency.
        """
        if self.canvas is None:
            return frame
            
        # Optimization: Only process if there is drawing content
        # Check simple grayscale threshold sum instead of countNonZero if faster, 
        # but countNonZero is optimized in C++.
        # Let's perform a fast check.
        
        imgGray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(imgGray, 10, 255, cv2.THRESH_BINARY)
        
        if cv2.countNonZero(mask) == 0:
            return frame
            
        # Fast Blending
        # Instead of full frame addWeighted, let's use numpy masking which is often faster for sparse updates?
        # Actually cv2.addWeighted is highly optimized (SIMD). 
        # The bottleneck is likely processing 1080p.
        
        # Opaque Blending (Fastest) - if user allows opacity to be 1.0
        # return cv2.add(frame, self.canvas) # This adds pixel values, can saturate.
        
        # Translucent Blending Optimized:
        # 1. Create colored overlay only (frame + canvas)
        # 1. Check if there is anything to draw (Mask check)
        # Using numpy.any is fast.
        mask = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        
        # Improvement: If bounding box of mask is small, crop before blending.
        # Finding contours is cheap on binary mask.
        points = cv2.findNonZero(mask)
        if points is None:
            return frame # Nothing drawn
            
        # Get bounding rect of drawing
        x, y, w, h = cv2.boundingRect(points)
        
        # Expand slightly to be safe
        h_frame, w_frame = frame.shape[:2]
        x = max(0, x - 2)
        y = max(0, y - 2)
        w = min(w_frame - x, w + 4)
        h = min(h_frame - y, h + 4)
        
        # ROI Slices
        frame_roi = frame[y:y+h, x:x+w]
        canvas_roi = self.canvas[y:y+h, x:x+w]
        mask_roi = mask[y:y+h, x:x+w]
        
        # Blend ONLY the ROI
        overlay_roi = cv2.addWeighted(frame_roi, 1.0, canvas_roi, DRAWING_OPACITY, 0)
        
        # Masked Copy in ROI
        mask_bool = mask_roi > 0
        mask_3c = np.stack([mask_bool] * 3, axis=2)
        
        frame_roi[mask_3c] = overlay_roi[mask_3c]
        
        # Put back into frame (Numpy reference update)
        frame[y:y+h, x:x+w] = frame_roi
        return frame

    def set_color(self, color):
        """
        Set the drawing color.
        
        Args:
            color: BGR tuple for the drawing color
        """
        self.draw_color = color
        self.brush_thickness = DRAWING_THICKNESS
        print(f"Drawing color set to: {color}")

    def set_eraser(self):
        """Set eraser mode."""
        self.draw_color = ERASER_COLOR
        self.brush_thickness = ERASER_THICKNESS
        print("Eraser mode activated")

    def clear(self):
        """Clear the drawing canvas."""
        self.canvas = None

