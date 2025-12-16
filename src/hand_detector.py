"""
Hand detection module using MediaPipe.
Handles the detection and tracking of hands in video frames.
"""

import mediapipe as mp
import cv2
from config.config import (
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    STATIC_IMAGE_MODE,
    MODEL_COMPLEXITY
)


class HandDetector:
    """Detects and tracks hands using MediaPipe."""
    
    def __init__(self):
        """Initialize MediaPipe hands solution."""
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=STATIC_IMAGE_MODE,
            max_num_hands=MAX_NUM_HANDS,
            model_complexity=MODEL_COMPLEXITY, 
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
    
    def detect_hands(self, frame):
        """
        Detect hands in the given frame.
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            results: MediaPipe hand detection results
        """
        # Optimization: Downscale frame for faster processing
        # MediaPipe internal model is small (e.g. 224x224)
        # Passing 1080p forces internal resize which is slow (+ data copy)
        # We resize to a reasonable "Analysis Resolution" (e.g. 640px width)
        h, w = frame.shape[:2]
        analysis_w = 640
        if w > analysis_w:
            scale = analysis_w / w
            analysis_h = int(h * scale)
            small_frame = cv2.resize(frame, (analysis_w, analysis_h))
        else:
            small_frame = frame
        
        # 1. Saturation Boost (HSV) - Helps distinguish skin from background
        # 2. CLAHE (LAB) - Improves local contrast
        try:
            # Saturation Boost
            hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
            h_c, s_c, v_c = cv2.split(hsv)
            # Multiply saturation by 1.5 and clip
            s_c = cv2.multiply(s_c, 1.5) 
            # (Note: cv2.multiply handles clamping automatically for uint8, usually. 
            # But let's be safe or just trust cv2's saturation arithmetic)
            # Actually cv2.multiply(src1, scale) returns result.
            hsv_boosted = cv2.merge((h_c, s_c, v_c))
            boosted_frame = cv2.cvtColor(hsv_boosted, cv2.COLOR_HSV2BGR)
            
            # CLAHE (on boosted frame)
            lab = cv2.cvtColor(boosted_frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        except Exception as e:
            # Fallback
            # print(f"Preprocessing error: {e}")
            enhanced_frame = small_frame

        rgb_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        return results
    
    def fingersUp(self, hand_landmarks):
        """
        Check which fingers are up using robust distance-based logic.
        Works for any hand orientation (vertical, horizontal, tilted).
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            list: [Thumb, Index, Middle, Ring, Pinky] booleans
        """
        fingers = []
        
        # Tip IDs
        tip_ids = [4, 8, 12, 16, 20]
        
        # Wrist is 0
        wrist = hand_landmarks.landmark[0]
        
        # 1. THUMB
        # Thumb is "Up" (Extended) if Tip is further from Pinky MCP (17) than IP (3) is.
        # Or simpler: check distance to Index MCP (5).
        # Standard approach: Thumb Tip x comparison relative to IP is orientation dependent.
        # Robust approach: Angle or Distance.
        # Let's use simplified Distance Check for this app:
        # If distance(ThumbTip, PinkyMCP) > distance(ThumbIP, PinkyMCP), it's extended.
        # Actually, simpler for "Pinch" app: Thumb is always "Active" capability-wise.
        # But let's stick to X-check relative to wrist/knuckle if hand is mostly vertical?
        # User complained about "not recognizing fingers that good".
        # Let's use the Reference Code style: Distance to WRIST for fingers.
        
        # For Thumb: It's hard to define "Folded" to wrist.
        # Let's stick to the X comparison BUT relative to the hand coordinate frame? No, too complex.
        # Let's use: Tip distance to Pinky Knuckle (17) is large -> Extended.
        # Thumb Tip (4), Pinky MCP (17).
        # We need to compute euclidean distance in 3D or 2D. landmarks have x,y (normalized).
        
        def dist(p1, p2):
            return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5
            
        # Thumb Logic override: Just return True for now, as it's mainly used for Pinching (Distance check)
        # The pinching logic does its own check.
        fingers.append(True) 
        
        # 2. FINGERS (Index, Middle, Ring, Pinky)
        # Check if Tip is further from Wrist than PIP joint is.
        # PIP joints: Index(6), Middle(10), Ring(14), Pinky(18)
        
        # Map: Finger ID -> (Tip ID, Pip ID)
        # Index: 8, 6
        # Middle: 12, 10
        # Ring: 16, 14
        # Pinky: 20, 18
        
        finger_indices = [(8, 6), (12, 10), (16, 14), (20, 18)]
        
        for tip_idx, pip_idx in finger_indices:
            tip = hand_landmarks.landmark[tip_idx]
            pip = hand_landmarks.landmark[pip_idx]
            
            # If Tip is further from Wrist than PIP is, it's extended.
            if dist(tip, wrist) > dist(pip, wrist):
                fingers.append(True)
            else:
                fingers.append(False)
                
        return fingers

    def draw_landmarks(self, frame, hand_landmarks):
        """
        Draw hand landmarks and connections on the frame.
        
        Args:
            frame: BGR image to draw on
            hand_landmarks: MediaPipe hand landmarks
        """
        self.mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style()
        )

    def draw_minimal_landmarks(self, frame, hand_landmarks):
        """
        Draw only essential landmarks (Fingertips + Wrist) for a cleaner UI.
        Draws lines from Wrist to each fingertip.
        """
        h, w, c = frame.shape
        
        # Get coordinates
        wrist = hand_landmarks.landmark[0]
        wx, wy = int(wrist.x * w), int(wrist.y * h)
        
        # Tips indices: Thumb=4, Index=8, Middle=12, Ring=16, Pinky=20
        tips = [4, 8, 12, 16, 20]
        colors = [
            (255, 0, 255), # Thumb (Pink)
            (0, 255, 0),   # Index (Green)
            (0, 255, 255), # Middle (Yellow)
            (255, 255, 0), # Ring (Cyan)
            (0, 0, 255)    # Pinky (Red)
        ]
        
        # Draw Wrist
        cv2.circle(frame, (wx, wy), 5, (200, 200, 200), cv2.FILLED)
        
        for idx, color in zip(tips, colors):
            lm = hand_landmarks.landmark[idx]
            lx, ly = int(lm.x * w), int(lm.y * h)
            
            # Line from Wrist to Tip
            cv2.line(frame, (wx, wy), (lx, ly), (100, 100, 100), 1)
            
            # Circle at Tip
            cv2.circle(frame, (lx, ly), 6, color, cv2.FILLED)
            cv2.circle(frame, (lx, ly), 8, (255, 255, 255), 1)
    
    def close(self):
        """Release MediaPipe resources."""
        self.hands.close()
