import os
import config

class ObjectDetector:
    def __init__(self, model_name="yolov8n.pt", device="cpu"):
        """
        Initialize the YOLO object detector.
        """
        self.model_name = model_name
        self.device = device
        
        print(f"Initializing YOLO Model '{self.model_name}' on '{self.device}'...")
        
        # We import YOLO inside to avoid slowing down imports globally
        from ultralytics import YOLO
        
        # Ultralytics handles downloading the weights automatically.
        # We ensure it looks in/downloads to the correct models directory to keep root clean.
        model_path = os.path.join(config.MODELS_DIR, self.model_name)
        
        try:
            self.model = YOLO(model_path)
            self.model.to(self.device)
            print("YOLO model loaded successfully.")
        except Exception as e:
            print(f"Error: Could not load YOLO model '{self.model_name}'. Details: {e}")
            import sys
            sys.exit(1)

    def detect(self, frame):
        """
        Detect objects in a frame using YOLO.
        Returns a list of detections containing bounding boxes, confidence, and classes.
        """
        # Run YOLO inference with configuration settings
        results = self.model(
            frame,
            conf=config.CONFIDENCE_THRESHOLD,
            imgsz=config.IMAGE_SIZE,
            device=self.device,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Extract coordinates, confidence, and class
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = result.names[cls_id]
                
                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "confidence": conf,
                    "class_id": cls_id,
                    "class_name": cls_name
                })
        
        inference_speed = 0.0
        if len(results) > 0 and hasattr(results[0], 'speed'):
            inference_speed = results[0].speed.get('inference', 0.0)
            
        raw_results = results[0] if len(results) > 0 else None
                
        return detections, inference_speed, raw_results
