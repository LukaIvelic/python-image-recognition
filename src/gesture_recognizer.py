"""
Gesture recognition module.
Analyzes hand landmarks to determine which gesture is being performed.
"""

from config.gestures import LANDMARK_INDICES, GESTURES, GESTURE_DISPLAY_NAMES


class GestureRecognizer:
    """Recognizes hand gestures based on finger positions."""
    
    def __init__(self):
        """Initialize the gesture recognizer."""
        self.landmarks_idx = LANDMARK_INDICES
        self.gestures = GESTURES
        self.display_names = GESTURE_DISPLAY_NAMES
    
    def is_finger_extended(self, landmarks, finger_tip_idx, finger_pip_idx, finger_mcp_idx=None):
        """
        Check if a finger is extended by comparing the y-coordinate of tip and PIP joint.
        Uses additional MCP check for better accuracy.
        
        Args:
            landmarks: List of hand landmarks
            finger_tip_idx: Index of the finger tip landmark
            finger_pip_idx: Index of the finger PIP joint landmark
            finger_mcp_idx: Index of the finger MCP joint landmark (optional)
            
        Returns:
            bool: True if finger is extended, False otherwise
        """
        # Primary check: tip must be above PIP
        tip_above_pip = landmarks[finger_tip_idx].y < landmarks[finger_pip_idx].y
        
        # Additional robustness: check with MCP joint for better accuracy
        if finger_mcp_idx is not None:
            # Tip should be significantly above MCP for extended finger
            tip_above_mcp = landmarks[finger_tip_idx].y < landmarks[finger_mcp_idx].y
            return tip_above_pip and tip_above_mcp
        
        return tip_above_pip
    
    def is_thumb_extended(self, landmarks, handedness):
        """
        Check if thumb is extended. Thumb uses x-coordinate for left/right hands.
        Uses more robust detection with distance threshold.
        
        Args:
            landmarks: List of hand landmarks
            handedness: "Left" or "Right"
            
        Returns:
            bool: True if thumb is extended, False otherwise
        """
        thumb_tip = landmarks[self.landmarks_idx['THUMB_TIP']]
        thumb_ip = landmarks[self.landmarks_idx['THUMB_IP']]
        
        # Calculate distance between tip and IP joint
        distance_x = abs(thumb_tip.x - thumb_ip.x)
        
        # Threshold for extended thumb (lowered for easier L sign detection)
        threshold = 0.02  # Lowered from 0.04
        
        # For right hand, thumb extends to the left (smaller x)
        # For left hand, thumb extends to the right (larger x)
        if handedness == "Right":
            return thumb_tip.x < thumb_ip.x and distance_x > threshold
        else:
            return thumb_tip.x > thumb_ip.x and distance_x > threshold
    
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
        
        # Sort gestures by priority (lower priority number = checked first)
        sorted_gestures = sorted(
            self.gestures.items(),
            key=lambda x: x[1].get('priority', 99)
        )
        
        # Try to match the finger pattern to a defined gesture
        for gesture_name, gesture_data in sorted_gestures:
            if gesture_data['exact_match']:
                if finger_states == gesture_data['fingers']:
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

