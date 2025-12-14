"""
AI Worker module.
Runs MediaPipe processing in a separate thread to decouple it from the display loop.
"""

import threading
import queue
import time
import copy
from src.hand_detector import HandDetector

class AIWorker:
    def __init__(self, recognizer):
        """
        Initialize the AI Worker.
        
        Args:
            recognizer: GestureRecognizer instance
        """
        self.recognizer = recognizer
        self.detector = None # Initialized in thread
        
        # Queue for incoming frames (size 1 to drop old frames)
        self.frame_queue = queue.Queue(maxsize=1)
        
        # Shared state for results
        self.latest_results = (None, []) # (processed_frame, gestures)
        self.results_lock = threading.Lock()
        
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the background thread."""
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop the background thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def submit_frame(self, frame):
        """
        Submit a frame for processing.
        Non-blocking: if worker is busy, this frame might be dropped (or replaces old).
        """
        if not self.running:
            return
            
        try:
            # Try to put frame. If full, remove old and put new.
            self.frame_queue.put_nowait(frame)
        except queue.Full:
            try:
                # Remove old frame to make space for newest
                _ = self.frame_queue.get_nowait()
                self.frame_queue.put_nowait(frame)
            except queue.Empty:
                pass # Should not happen given logic, but safe pass
                
    def get_results(self):
        """Get the latest available results."""
        with self.results_lock:
            # Return a generic copy/ref? 
            # Gestures is a list of dicts, frame is numpy array.
            # We don't want to deepcopy the frame every time if not needed.
            # But the 'processed_frame' might be modified by the detector (drawing landmarks?).
            # Actually, `detector.detect_hands` usually returns results, not a drawn frame.
            # But `App.process_frame` was drawing on it?
            # Let's check App logic.
            return self.latest_results

    def _process_loop(self):
        """Process frames from the queue."""
        # Initialize detector here to ensure Thread Affinity (MediaPipe requires this)
        self.detector = HandDetector()
        
        while self.running:
            try:
                # Wait for a frame
                frame = self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue
                
            # Process
            # Note: We should probably work on a copy if we modify it?
            # MediaPipe reads. `process_frame` in App currently does logic.
            # We need to move the logic here.
            
            # Since we can't call `self.process_frame` from App easily without circular deps or passing App,
            # We should replicate the logic or pass a function?
            # Passing detector/recognizer is cleaner.
            
            try:
                # 1. Detect
                # Note: HandDetector.detect_hands might resize internally but that's fine.
                hand_results = self.detector.detect_hands(frame)
                
                # 2. Recognize
                gestures = []
                frame_height, frame_width = frame.shape[:2]
                
                if hand_results.multi_hand_landmarks:
                    for hand_landmarks, handedness in zip(hand_results.multi_hand_landmarks, 
                                                        hand_results.multi_handedness):
                        
                        # Recognize
                        hand_label = handedness.classification[0].label
                        gesture_info = self.recognizer.recognize_gesture(
                            hand_landmarks.landmark, 
                            hand_label
                        )
                        
                        # Get action (logic from App previously)
                        confidence = gesture_info['confidence']
                        action_result = gesture_info['action']
                        
                        gestures.append({
                            'hand': hand_label,
                            'gesture': gesture_info['name'],
                            'action': action_result,
                            'confidence': confidence,
                            'landmarks': hand_landmarks, # Store for UI drawing
                            'handedness': handedness
                        })
                
                # Store results
                with self.results_lock:
                    self.latest_results = (frame, gestures) # Pass original frame ref or processed?
                    # We usually want the landmarks to draw them in the UI thread.
                    # We shouldn't draw landmarks *here* because that burns CPU on the AI thread for visuals.
                    # Better to pass landmarks back and let UI thread draw them.
            
            except Exception as e:
                print(f"AI Worker Error: {e}")
                
            finally:
                self.frame_queue.task_done()
