import torch
import numpy as np
from types import SimpleNamespace

class ObjectTracker:
    def __init__(self):
        """
        Initialize the ByteTrack object tracker.
        """
        print("Initializing ByteTrack ObjectTracker...")
        self.tracker = None
        try:
            # We use the existing ultralytics dependency for BYTETracker
            import config
            from ultralytics.trackers.byte_tracker import BYTETracker
            
            # Configuration settings for ByteTrack dynamically pulled
            args = SimpleNamespace(
                track_high_thresh=getattr(config, 'TRACKER_TRACK_HIGH_THRESH', 0.5),
                track_low_thresh=getattr(config, 'TRACKER_TRACK_LOW_THRESH', 0.1),
                new_track_thresh=getattr(config, 'TRACKER_NEW_TRACK_THRESH', 0.6),
                track_buffer=getattr(config, 'TRACKER_TRACK_BUFFER', 30),
                match_thresh=getattr(config, 'TRACKER_MATCH_THRESHOLD', 0.8),
                fuse_score=False,
                mot20=False
            )
            frame_rate = getattr(config, 'TRACKER_FRAME_RATE', 30)
            args.frame_rate = frame_rate
            self.tracker = BYTETracker(args=args)
        except Exception as e:
            print(f"Error loading ultralytics BYTETracker: {e}")

    def update(self, detections, frame, raw_results=None):
        """
        Update tracking state with new detections directly from YOLO results.
        """
        if self.tracker is None or raw_results is None or len(detections) == 0:
            return []

        # Update the tracker directly using the YOLO results object
        try:
            import torch
            res = raw_results[0] if isinstance(raw_results, list) else raw_results
            det = res.boxes if hasattr(res, 'boxes') and res.boxes is not None else None
            if det is None or len(det) == 0:
                return []
            tracked_objects = self.tracker.update(det, img=frame)
        except Exception as e:
            print(f"Tracker update error: {e}")
            return []

        results = []
        if tracked_objects is not None and len(tracked_objects) > 0:
            for obj in tracked_objects:
                if hasattr(obj, 'tlbr'):
                    x1, y1, x2, y2 = map(int, obj.tlbr)
                    track_id = int(obj.track_id)
                    conf = float(obj.score) if hasattr(obj, 'score') else 1.0
                    cls_id = int(obj.cls) if hasattr(obj, 'cls') else -1
                else:
                    # Handle output format safely (supports NumPy arrays returned by older ultralytics)
                    x1, y1, x2, y2 = map(int, obj[:4])
                    track_id = int(obj[4])
                    conf = float(obj[5]) if len(obj) > 5 else 1.0
                    cls_id = int(obj[6]) if len(obj) > 6 else -1

                # Recover the class name from original detections
                class_name = "object"
                for d in detections:
                    if d["class_id"] == cls_id or cls_id == -1:
                        class_name = d["class_name"]
                        break

                results.append({
                    "bbox": (x1, y1, x2, y2),
                    "track_id": track_id,
                    "class_id": cls_id,
                    "class_name": class_name,
                    "confidence": conf
                })

        return results
