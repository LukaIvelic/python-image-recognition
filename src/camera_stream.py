"""
Threaded Camera Stream module.
Reads frames in a separate thread to prevent I/O blocking.
"""

import cv2
from threading import Thread

class CameraStream:
    """Class for threaded video capture."""
    
    def __init__(self, src=0, width=1280, height=720):
        """
        Initialize the camera stream.
        
        Args:
            src: Camera index or video path
            width: Desired width
            height: Desired height
        """
        self.stream = cv2.VideoCapture(src)
        
        # Optimize resolution (try-catch in case not supported)
        try:
            # MJPG is usually required for high framerates on USB webcams
            self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Mac-specific optimization
            # self.stream.set(cv2.CAP_PROP_FPS, 30)
        except Exception:
            pass
            
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        
        # Determine actual resolution
        self.width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
    def start(self):
        """Start the thread to read frames."""
        t = Thread(target=self.update, args=())
        t.daemon = True # Daemon thread exits when main program exits
        t.start()
        return self
        
    def update(self):
        """Loop to continuously grab frames."""
        while True:
            if self.stopped:
                return
            
            # Read the next frame from the stream
            (grabbed, frame) = self.stream.read()
            if grabbed:
               self.frame = frame
            else:
               self.stopped = True
               
    def read(self):
        """Return the most recent frame."""
        return self.grabbed, self.frame
        
    def stop(self):
        """Stop the thread and release resources."""
        self.stopped = True
        self.stream.release()
        
    def isOpened(self):
        return self.stream.isOpened()
