import cv2

class VideoSource:
    def __init__(self, source=0):
        """
        Initialize video source (webcam or file).
        """
        self.source = source
        self.cap = None

    def start(self):
        """
        Start capturing from the video source.
        Returns True if successful, False otherwise.
        """
        self.cap = cv2.VideoCapture(self.source)
        return self.cap.isOpened()

    def read(self):
        """
        Read a single frame from the video source.
        Returns a tuple (success, frame).
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def release(self):
        """
        Release the video capture device.
        """
        if self.cap is not None:
            self.cap.release()
