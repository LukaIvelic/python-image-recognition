
import cv2
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.drawing_manager import DrawingManager

# Mock classes
class MockLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MockLandmarks:
    def __init__(self):
        self.landmark = [MockLandmark(0.5, 0.5) for _ in range(21)]

def test_drawing_update():
    print("Testing DrawingManager.update()...")
    dm = DrawingManager()
    
    # Mock Frame
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Mock Landmarks (NormalizedLandmarkList wrapper)
    landmarks = MockLandmarks()
    
    # Mock Fingers [Thumb, Index, Middle, Ring, Pinky]
    fingers = [True, True, False, False, False] # Pinch (Index+Thumb)
    
    try:
        dm.update(frame, landmarks, fingers)
        print("Update successful!")
    except Exception as e:
        print(f"Update failed: {e}")
        exit(1)

if __name__ == "__main__":
    test_drawing_update()
