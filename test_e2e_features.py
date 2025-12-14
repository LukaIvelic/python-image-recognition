
import cv2
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.hand_detector import HandDetector
from src.visualizer import Visualizer

# Mock classes for MediaPipe objects
class MockLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MockLandmarks:
    def __init__(self):
        # Create 21 landmarks
        self.landmark = [MockLandmark(0.5, 0.5) for _ in range(21)]

def test_robust_finger_detection():
    print("\n--- Testing Robust Finger Detection ---")
    hd = HandDetector()
    landmarks = MockLandmarks()
    
    # Test 1: All folded (Points at center, wrist at center)
    # Both Tip and Pip are 0.5, 0.5. Distance is equal.
    # Current logic: Tip further from Wrist than PIP.
    # To simulate "Extended", Tip must be further.
    
    # Set Wrist
    landmarks.landmark[0] = MockLandmark(0.5, 0.9) # Bottom center
    
    # Set Index Finger (Tip 8, Pip 6)
    # Case A: Extended (Tip Higher/Further)
    landmarks.landmark[6] = MockLandmark(0.5, 0.7)
    landmarks.landmark[8] = MockLandmark(0.5, 0.4) # Further from wrist
    
    fingers = hd.fingersUp(landmarks)
    # Index is index 1 in list [Thumb, Index, Middle, Ring, Pinky]
    if fingers[1]:
        print("Pass: Index correctly detected as Extended.")
    else:
        print("Fail: Index falsely detected as Folded.")
        
    # Case B: Folded (Tip Closer than PIP to wrist)
    landmarks.landmark[8] = MockLandmark(0.5, 0.8) # Closer to wrist (0.9) than Pip (0.7)
    fingers = hd.fingersUp(landmarks)
    if not fingers[1]:
        print("Pass: Index correctly detected as Folded.")
    else:
        print("Fail: Index falsely detected as Extended.")

def test_visualizer_glass_ui():
    print("\n--- Testing Visualizer Glass UI ---")
    vis = Visualizer()
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    try:
        vis.draw_ui_overlay(frame, "TEST_MODE", True)
        print("Pass: UI Overlay drew without error.")
    except Exception as e:
        print(f"Fail: UI Overlay Error: {e}")

if __name__ == "__main__":
    test_robust_finger_detection()
    test_visualizer_glass_ui()
