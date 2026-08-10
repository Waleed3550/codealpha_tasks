import cv2

class Visualizer:
    def __init__(self):
        """
        Initialize visualization tools.
        """
        pass

    def draw_annotations(self, frame, tracks):
        """
        Draw bounding boxes, labels, and tracking IDs on the frame.
        """
        for track in tracks:
            x1, y1, x2, y2 = track["bbox"]
            conf = track["confidence"]
            label = track["class_name"]
            
            # Incorporate tracking ID into the label if available (Format: person | ID: 4 | 91%)
            conf_percent = int(conf * 100)
            if "track_id" in track:
                text = f"{label} | ID: {track['track_id']} | {conf_percent}%"
            else:
                text = f"{label} | {conf_percent}%"
            
            # Draw bounding box (Green)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Background rectangle for text for better readability
            (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x1, max(y1 - h - 10, 0)), (x1 + w, max(y1, 10)), (0, 255, 0), -1)
            
            # Draw text (Black text on green background)
            cv2.putText(frame, text, (x1, max(y1 - 5, 5)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
        return frame

    def draw_fps(self, frame, fps):
        """Draw FPS on the top-left corner."""
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        return frame
        
    def draw_object_count(self, frame, count):
        """Draw Tracked Objects count below the FPS."""
        cv2.putText(frame, f"Tracked Objects: {count}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        return frame

    def draw_inference_speed(self, frame, speed_ms):
        """Draw YOLO inference speed below object count."""
        cv2.putText(frame, f"Inference: {speed_ms:.1f}ms", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        return frame
