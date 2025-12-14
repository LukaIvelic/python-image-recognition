
import cv2
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.mouse_controller import MouseController

def test_mirroring_mapping():
    print("\n--- Testing Mirror Mapping ---")
    mc = MouseController(screen_width=1920, screen_height=1080)
    
    # Scenario: Mirror View is Enabled (handled by App flipping frame)
    # The MouseController receives `hand_x`.
    # If I engage "Mirror Mode":
    # My Real Right Hand is on the Right Side of the Screen.
    # The camera (if mirrored) shows hand on Right (img_x ~ 1.0)
    # So MouseController sees x=1.0.
    # Cursor should go to Right (screen_x ~ 1920).
    
    # Test Input x=1.0 (Right edge of camera frame)
    sx, sy = mc.hand_to_screen_coords(1.0, 0.5, 640, 480)
    print(f"Input(1.0, 0.5) -> Output({sx}, {sy})")
    
    # If logic is correct (Direct mapping), output should be Max Width
    if abs(sx - 1920) < 5:
        print("Pass: Right Camera Edge maps to Right Screen Edge.")
    else:
        print(f"Fail: Right Camera Edge maps to {sx} (Expected ~1920).")
        exit(1)
        
    # Test Input x=0.0 (Left edge)
    sx, sy = mc.hand_to_screen_coords(0.0, 0.5, 640, 480)
    if sx < 5:
        print("Pass: Left Camera Edge maps to Left Screen Edge.")
    else:
        print(f"Fail: Left Camera Edge maps to {sx}.")
        exit(1)

if __name__ == "__main__":
    test_mirroring_mapping()
