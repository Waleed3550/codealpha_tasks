import time

class FPSCounter:
    def __init__(self):
        self.prev_time = time.time()
        
    def update(self):
        """Calculates and returns the current FPS."""
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time + 1e-6)
        self.prev_time = current_time
        return fps
