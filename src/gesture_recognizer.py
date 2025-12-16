"""
Gesture recognition module.
Analyzes hand landmarks to determine which gesture is being performed.
"""

import math
from config.gestures import LANDMARK_INDICES, GESTURES, GESTURE_DISPLAY_NAMES
from config.config import PINCH_THRESHOLD, FINGER_PAIR_THRESHOLD


class GestureRecognizer:
    """Recognizes hand gestures based on finger positions."""
    
    def __init__(self):
        """Initialize the gesture recognizer."""
        self.landmarks_idx = LANDMARK_INDICES
        self.gestures = GESTURES
        self.display_names = GESTURE_DISPLAY_NAMES
        
    def calculate_hand_scale(self, landmarks):
        """
        Calculate scale of hand using distance between Wrist and Middle Finger MCP.
        This provides a reference size to make thresholds scale-invariant.
        """
        wrist = landmarks[0]
        middle_mcp = landmarks[self.landmarks_idx['MIDDLE_TIP']] # Using Tip for larger scale, or MCP? 
        # Actually PIP is more stable than tip. MCP (0-9) is standard palm size ref.
        # Let's use Wrist (0) to Middle MCP (9).
        middle_mcp = landmarks[9] # Hardcoded 9 for Middle MCP
        
        scale = math.hypot(middle_mcp.x - wrist.x, middle_mcp.y - wrist.y)
        return scale
    
    def is_finger_extended(self, landmarks, finger_tip_idx, finger_pip_idx, finger_mcp_idx=None):
        """
        Check if a finger is extended using Euclidean distance from wrist.
        Rotation invariant.
        """
        wrist = landmarks[0]
        tip = landmarks[finger_tip_idx]
        pip = landmarks[finger_pip_idx]
        
        # Calculate distance from wrist to tip and wrist to PIP
        dist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        dist_pip = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
        
        # Finger is extended if Tip is further from Wrist than PIP
        # Add a small buffer for stability
        return dist_tip > (dist_pip * 1.05) # Tip must be 5% further than PIP
    
    def is_thumb_extended(self, landmarks, handedness=None):
        """
        Check if thumb is extended.
        Requires:
        1. Tip further from Wrist than IP (Standard Length Check)
        2. Tip NOT close to Index Finger Base (Proximity Check)
           - This distinguishes "Index Up" (tucked thumb) from "Gun" (extended thumb).
        """
        wrist = landmarks[0]
        tip = landmarks[self.landmarks_idx['THUMB_TIP']]
        ip = landmarks[self.landmarks_idx['THUMB_IP']]
        mcp = landmarks[self.landmarks_idx['THUMB_MCP']]
        
        # Reference point: Index MCP (Base of index finger)
        index_mcp = landmarks[self.landmarks_idx['INDEX_MCP']]
        
        # 1. Standard Length Check (Extended outwards from wrist)
        dist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        dist_ip = math.hypot(ip.x - wrist.x, ip.y - wrist.y)
        dist_mcp = math.hypot(mcp.x - wrist.x, mcp.y - wrist.y)
        is_long_enough = dist_tip > dist_ip and dist_tip > dist_mcp
        
        # 2. Proximity Check (Is it tucked?)
        # Calculate scale reference (Wrist to Index MCP)
        scale_ref = math.hypot(index_mcp.x - wrist.x, index_mcp.y - wrist.y)
        
        # Distance between Thumb Tip and Index MCP
        thumb_index_dist = math.hypot(tip.x - index_mcp.x, tip.y - index_mcp.y)
        
        # If thumb tip is too close to index base, it's tucked.
        # If thumb tip is too close to index base, it's tucked.
        # Threshold: 0.5 * scale_reference works well generally.
        # Reduced to 0.4 to allow "Gun" gesture where thumb might be slightly more tucked/angled
        # Raised to 0.45 to reduce false positives (Index misidentified as Gun)
        is_sticking_out = thumb_index_dist > (0.45 * scale_ref)
        
        return is_long_enough and is_sticking_out
    
    def get_finger_states(self, landmarks, handedness):
        """
        Get the extended/closed state of all fingers.
        
        Args:
            landmarks: List of hand landmarks
            handedness: "Left" or "Right"
            
        Returns:
            list: [thumb, index, middle, ring, pinky] - True if extended
        """
        thumb = self.is_thumb_extended(landmarks, handedness)
        index = self.is_finger_extended(
            landmarks, 
            self.landmarks_idx['INDEX_TIP'],
            self.landmarks_idx['INDEX_PIP'],
            self.landmarks_idx['INDEX_MCP']
        )
        middle = self.is_finger_extended(
            landmarks,
            self.landmarks_idx['MIDDLE_TIP'],
            self.landmarks_idx['MIDDLE_PIP'],
            self.landmarks_idx['MIDDLE_MCP']
        )
        ring = self.is_finger_extended(
            landmarks,
            self.landmarks_idx['RING_TIP'],
            self.landmarks_idx['RING_PIP'],
            self.landmarks_idx['RING_MCP']
        )
        pinky = self.is_finger_extended(
            landmarks,
            self.landmarks_idx['PINKY_TIP'],
            self.landmarks_idx['PINKY_PIP'],
            self.landmarks_idx['PINKY_MCP']
        )
        
        return [thumb, index, middle, ring, pinky]
    
    def recognize_gesture(self, landmarks, handedness):
        """
        Recognize hand gesture based on finger positions.
        
        Args:
            landmarks: List of hand landmarks
            handedness: "Left" or "Right"
            
        Returns:
            dict: Dictionary with gesture info including name, action, and key
        """
        finger_states = self.get_finger_states(landmarks, handedness)
        
        # Calculate Hand Scale (Reference Size)
        hand_scale = self.calculate_hand_scale(landmarks)
        
        # --- 1. PRIORITY PINCH CHECK (Dynamic Threshold) ---
        # Fixed threshold (PINCH_THRESHOLD) works for average distance.
        # Dynamic: threshold = hand_scale * factor
        # If scale is 0.2 (normal), thresh 0.05 is 0.25x scale.
        
        pinch_threshold_dynamic = hand_scale * 0.3 # Reduce to 0.3 for tighter consistency?
        # Let's keep a minimum to prevent issues at very far distances
        pinch_threshold_dynamic = max(0.02, pinch_threshold_dynamic)
        
        # Check distance between Index Tip and Thumb Tip
        idx_tip = landmarks[self.landmarks_idx['INDEX_TIP']]
        thumb_tip = landmarks[self.landmarks_idx['THUMB_TIP']]
        
        # Calculate Euclidean distance
        distance = math.hypot(idx_tip.x - thumb_tip.x, idx_tip.y - thumb_tip.y)
        
        if distance < pinch_threshold_dynamic:
            # Overrides everything else - Pinch is now MOVE
            return {
                'name': 'MOVING (Pinch)',
                'action': 'move_cursor',
                'gesture_key': 'CURSOR_CONTROL',
                'confidence': 1.0
            }
        
        # --- 2. SCROLL ACTIVATION (Index + Middle Together) - Dynamic ---
        idx_tip = landmarks[self.landmarks_idx['INDEX_TIP']]
        mid_tip = landmarks[self.landmarks_idx['MIDDLE_TIP']]
        
        pair_dist = math.hypot(idx_tip.x - mid_tip.x, idx_tip.y - mid_tip.y)
        
        pair_dist = math.hypot(idx_tip.x - mid_tip.x, idx_tip.y - mid_tip.y)
        
        pair_threshold_dynamic = hand_scale * 0.6 # Increased to 0.6 for very easy activation
        
        if finger_states[1] and finger_states[2] and pair_dist < pair_threshold_dynamic:
            # Check Ring finger state (must be closed for 2-finger scroll)
            if not finger_states[3]: 
                return {
                    'name': 'SCROLL MODE',
                    'action': 'scroll_active',
                    'gesture_key': 'SCROLL_ACTIVE',
                    'confidence': 1.0
                }

        # --- 3. Standard Finger State Matching ---
        # Sort gestures by priority (lower priority number = checked first)
        sorted_gestures = sorted(
            self.gestures.items(),
            key=lambda x: x[1].get('priority', 99)
        )
        
        # Try to match the finger pattern to a defined gesture
        for gesture_name, gesture_data in sorted_gestures:
            if gesture_data['exact_match']:
                if finger_states == gesture_data['fingers']:
                    
                    # --- FIX: DOUBLE CLICK (Gun) False Positive Check ---
                    # Prevent "Spread Pinch" (Thumb and Index close but not touching) from detected as Gun.
                    # Gun gesture requires checking distance between Index Tip and Thumb Tip.
                    # It must be LARGE (Thumb extended UP, Index extended FORWARD).
                    if gesture_name == 'DOUBLE_CLICK':
                         idx_tip = landmarks[self.landmarks_idx['INDEX_TIP']]
                         thumb_tip = landmarks[self.landmarks_idx['THUMB_TIP']]
                         dist_idx_thumb = math.hypot(idx_tip.x - thumb_tip.x, idx_tip.y - thumb_tip.y)
                         
                         # Threshold: Distance must be significant (e.g. > 1.0x Hand Scale)
                         # If they are close, it's likely a "loose pinch", not a gun.
                         if dist_idx_thumb < (hand_scale * 1.0):
                             continue # Skip this match, it's not a real Gun


                    return {
                        'name': self.display_names.get(gesture_name, gesture_name),
                        'action': gesture_data.get('action', 'none'),
                        'gesture_key': gesture_name,
                        'confidence': 1.0 # Default confidence for rule-based
                    }
        
        # If no match found, return UNKNOWN
        return {
            'name': 'UNKNOWN',
            'action': 'none',
            'gesture_key': 'UNKNOWN',
            'confidence': 0.0
        }

