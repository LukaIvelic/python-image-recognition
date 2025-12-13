"""
Configuration settings for hand gesture recognition system.
"""

# Camera Settings
CAMERA_INDEX = 0
MIRROR_VIEW = False  # Flip frame horizontally for mirror effect

# MediaPipe Hand Detection Settings
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
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
HAND_PADDING_X = 0  # Horizontal padding (0.0 - 0.4)
HAND_PADDING_Y = 0  # Vertical padding (0.0 - 0.4)