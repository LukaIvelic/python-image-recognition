"""
Gesture definitions and recognition rules for mouse control.

Each gesture is defined by which fingers are extended.
Finger order: [Thumb, Index, Middle, Ring, Pinky]
"""

# Landmark indices for MediaPipe hand tracking
# Landmark indices for MediaPipe hand tracking
# Landmark indices for MediaPipe hand tracking
LANDMARK_INDICES = {
    'THUMB_TIP': 4,
    'THUMB_IP': 3,
    'THUMB_MCP': 2,
    'INDEX_TIP': 8,
    'INDEX_PIP': 6,
    'INDEX_MCP': 5,
    'MIDDLE_TIP': 12,
    'MIDDLE_PIP': 10,
    'MIDDLE_MCP': 9,
    'RING_TIP': 16,
    'RING_PIP': 14,
    'RING_MCP': 13,
    'PINKY_TIP': 20,
    'PINKY_PIP': 18,
    'PINKY_MCP': 17,
    'WRIST': 0
}

# Mouse control gesture definitions
GESTURES = {
    'DRAG': {
        'fingers': [False, False, False, False, False],
        'description': 'Fist - Drag (Mouse Down + Move)',
        'action': 'drag',
        'exact_match': True,
        'priority': 1
    },
    'DOUBLE_CLICK': {
        'fingers': [True, True, False, False, False],
        'description': 'Gun (Thumb+Index) - Double Click',
        'action': 'double_click',
        'exact_match': True,
        'priority': 2
    },
    'CURSOR_CONTROL': {
        'fingers': [False, True, False, False, False],
        'description': 'Index finger - Fallback Move',
        'action': 'none', # Handled by Pinch
        'exact_match': True,
        'priority': 99
    },
    'LEFT_CLICK': {
        'fingers': [False, True, False, False, False],
        'description': 'Index Finger - Left Click',
        'action': 'left_click',
        'exact_match': True,
        'priority': 2
    },
    'RIGHT_CLICK': {
        'fingers': [False, True, True, False, False],
        'description': 'Peace Sign - Right Click',
        'action': 'right_click',
        'exact_match': True,
        'priority': 2
    },
    'SCROLL_UP': {
        'fingers': [False, True, True, True, False],
        'description': 'Three fingers - Scroll up',
        'action': 'scroll_up',
        'exact_match': True,
        'priority': 2
    },
    'SCROLL_DOWN': {
        'fingers': [False, True, True, True, True],
        'description': 'Four fingers - Scroll down',
        'action': 'scroll_down',
        'exact_match': True,
        'priority': 2
    },

    'STOP': {
        'fingers': [True, True, True, True, True],
        'description': 'Open hand - Stop all actions',
        'action': 'stop',
        'exact_match': True,
        'priority': 1
    }
}

# Gesture display names (for better terminal output)
GESTURE_DISPLAY_NAMES = {
    'DRAG': 'DRAG (Fist)',
    'DOUBLE_CLICK': 'DOUBLE CLICK (Gun)',
    'CURSOR_CONTROL': 'PINCH TO MOVE',
    'LEFT_CLICK': 'LEFT CLICK (Index)',
    'RIGHT_CLICK': 'RIGHT CLICK (Peace)',
    'SCROLL_UP': 'SCROLL UP (3 fingers)',
    'SCROLL_DOWN': 'SCROLL DOWN (4 fingers)',
    'STOP': 'STOP'
}

def get_gesture_list():
    """Returns a formatted list of all recognizable gestures."""
    gesture_list = []
    for name, data in GESTURES.items():
        display_name = GESTURE_DISPLAY_NAMES.get(name, name)
        gesture_list.append(f"  - {display_name}: {data['description']}")
    return gesture_list
