"""
Configuration settings for hand gesture recognition system.
"""

# Camera Settings
CAMERA_INDEX = 0
MIRROR_VIEW = True  # Flip frame horizontally for mirror effect

# MediaPipe Initialization
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.8 # Raised for better stability
MIN_TRACKING_CONFIDENCE = 0.8
MODEL_COMPLEXITY = 1 # 0=Lite, 1=Full
STATIC_IMAGE_MODE = False

# Display Settings
WINDOW_NAME = "Hand Gesture Recognition"
FONT = 1  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1
FONT_COLOR = (0, 255, 0)  # Green
FONT_THICKNESS = 2
TEXT_Y_OFFSET = 30
TEXT_LINE_HEIGHT = 40

# Terminal Output Settings
TERMINAL_WIDTH = 60
SEPARATOR_CHAR = "="

# Mouse Control Settings
ENABLE_MOUSE_CONTROL = True
MOUSE_SMOOTHING = 1  # 0 = no smoothing, 1 = max smoothing
CLICK_COOLDOWN = 1  # seconds between clicks
SCROLL_COOLDOWN = 0.025  # seconds between scrolls
SCROLL_AMOUNT = 50  # Scroll sensitivity

# Hand detection padding (keeps hand in camera view while reaching screen edges)
# 0.15 = use center 70% of camera for full screen control
# Lower = need more hand movement, Higher = need less hand movement
HAND_PADDING_X = 0.25  # Horizontal padding (0.0 - 0.4) - Increased for easier corner reach
HAND_PADDING_Y = 0.25  # Vertical padding (0.0 - 0.4)

# Gesture Thresholds
PINCH_THRESHOLD = 0.05  # Distance between index and thumb for click
PINCH_RELEASE_THRESHOLD = 0.15  # Distance to release click (hysteresis) - Increased for stability during fast drags
SCROLL_ACTIVATION_THRESHOLD = 0.12 # "Near Pinch" distance to activate scroll mode (deprecated but kept for ref if needed)
FINGER_PAIR_THRESHOLD = 0.06 # Distance between fingers to consider them "together"
GESTURE_TRIGGER_DELAY = 0.5  # Default/Fallback delay
GESTURE_TRIGGER_DELAY_CLICK = 0.5 # Standard delay for Left/Right click
GESTURE_TRIGGER_DELAY_DOUBLE = 0.8 # Longer delay for Double Click (Safety)
SCROLL_SPEED_MULTIPLIER = 30.0 # Speed factor for joystick scrolling
MOVEMENT_GRACE_PERIOD = 0.3 # Seconds to wait after moving before accepting clicks (Debounce)

# Drawing Mode Settings
DRAWING_MODE_KEY = 'd'
CLEAR_SCREEN_KEY = 'c'
VIRTUAL_CAMERA_ENABLED = True
HEADER_HEIGHT = 125

# Colors (B, G, R)
DRAWING_COLOR_PINK = (255, 0, 255)
DRAWING_COLOR_BLUE = (255, 0, 0)
DRAWING_COLOR_GREEN = (0, 255, 0)
ERASER_COLOR = (0, 0, 0)

DEFAULT_DRAWING_COLOR = DRAWING_COLOR_PINK
DRAWING_THICKNESS = 5
ERASER_THICKNESS = 50

# Smoothing
SMOOTHING_FACTOR = 0.5  # Increased for faster response (less lag)

# Visuals
DRAWING_OPACITY = 1.0  # Solid lines (no transparency)