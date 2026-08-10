import os
import cv2
import time
import threading
import logging
from datetime import datetime

import config
from detection.detector import ObjectDetector
from tracking.tracker import ObjectTracker
from video.video_source import VideoSource
from visualization.visualizer import Visualizer
from utils.helpers import FPSCounter
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class ProcessingService:
    def __init__(self):
        self.detector = None
        self.tracker = None
        self.visualizer = Visualizer()
        self.video_src = None
        
        self.is_running = False
        self.is_recording = False
        self.video_writer = None
        
        self.lock = threading.Lock()
        
        self.fps_counter = FPSCounter()
        self.current_fps = 0.0
        self.inference_time = 0.0
        self.total_detections = 0
        self.recent_objects = []
        self.tracked_count = 0
        
        self.current_frame = None
        
        self.db = DatabaseService()
        self.session_id = None
        
        self.session_start_time = None
        self.session_total_fps = 0.0
        self.session_fps_samples = 0
        self.session_total_confidence = 0.0
        self._pending_db_detections = []
        self.session_detection_count = 0
        self.frame_number = 0
        self.all_tracked_ids = set()

    def initialize_models(self):
        if self.detector is None:
            logger.info("Initializing YOLO model...")
            self.detector = ObjectDetector(model_name=config.MODEL_NAME, device=config.DEVICE)
        if self.tracker is None:
            logger.info("Initializing ByteTrack tracker...")
            self.tracker = ObjectTracker()

    def start_stream(self, source=0):
        with self.lock:
            if self.is_running:
                logger.warning("Attempted to start stream, but it is already running.")
                return False, "Already running"
            
            try:
                self.initialize_models()
                self.video_src = VideoSource(source=source)
                if not self.video_src.start():
                    raise ValueError(f"Could not open video source: {source}")
            except Exception as e:
                logger.error(f"Error starting video stream: {e}")
                return False, f"Error starting stream: {e}"

            self.is_running = True
            self.total_detections = 0
            self.recent_objects = []
            self.fps_counter = FPSCounter()
            self.frame_number = 0
            # Wait for previous thread to finish cleanup if it exists
            if hasattr(self, '_thread') and self._thread is not None and self._thread.is_alive():
                self.lock.release()
                self._thread.join()
                self.lock.acquire()

            self.all_tracked_ids = set()
            self.session_total_fps = 0.0
            self.session_fps_samples = 0
            self.session_total_confidence = 0.0
            self.session_detection_count = 0
            self.session_start_time = time.time()
            
            input_type = 'camera' if isinstance(source, int) or str(source).isdigit() else 'video'
            source_name = str(source)
            self.session_id = self.db.create_session(input_type, source_name)
            logger.info(f"Started processing session {self.session_id} on {input_type} {source_name}")
            
            self._thread = threading.Thread(target=self._process_loop, daemon=True)
            self._thread.start()
            return True, "Started successfully"

    def stop_stream(self, status='stopped'):
        with self.lock:
            if not self.is_running:
                return False, "Not running"
                
            logger.info("Signaling video processing stream to stop...")
            self.is_running = False
            self._pending_stop_status = status
            
            return True, "Stopped successfully"

    def _cleanup_stream(self, status='stopped'):
        with self.lock:
            if self.is_recording and self.video_writer:
                self.video_writer.release()
                self.is_recording = False
            
            if self.video_src:
                self.video_src.release()
                self.video_src = None
            
            # Close OpenCV windows if desktop mode was being used
            cv2.destroyAllWindows()
                
            if self.session_id is not None:
                # Save any remaining pending detections before ending
                if self._pending_db_detections:
                    self.db.save_detections(self.session_id, self._pending_db_detections)
                    self._pending_db_detections.clear()
                    
                processing_time = time.time() - self.session_start_time if self.session_start_time else 0
                avg_fps = self.session_total_fps / self.session_fps_samples if self.session_fps_samples > 0 else 0
                avg_conf = self.session_total_confidence / self.session_detection_count if self.session_detection_count > 0 else 0
                
                self.db.end_session(
                    session_id=self.session_id,
                    status=status,
                    total_detections=self.total_detections,
                    total_tracked_objects=len(self.all_tracked_ids),
                    avg_confidence=avg_conf,
                    avg_fps=avg_fps,
                    processing_time=processing_time
                )
                logger.info(f"Session {self.session_id} ended with status {status}")
                self.session_id = None

    def start_recording(self):
        with self.lock:
            if not self.is_running or self.current_frame is None:
                return False, "No active stream to record"
            try:
                if self.current_frame is None:
                    return False, "No frame available to start recording"
                    
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                session_prefix = f"session_{self.session_id}_" if self.session_id else ""
                filename = f"{session_prefix}{timestamp_str}.mp4"
                output_path = os.path.join(config.RECORDINGS_DIR, filename)
                
                h, w = self.current_frame.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(output_path, fourcc, 30.0, (w, h))
                self.is_recording = True
                
                if self.session_id:
                    self.db.update_session_metadata(self.session_id, output_video=output_path)
                    
                logger.info(f"Started video recording to {output_path}")
                return True, "Recording started"
            except Exception as e:
                logger.error(f"Error starting recording: {e}")
                return False, f"Failed to start recording: {e}"

    def stop_recording(self):
        with self.lock:
            if not self.is_recording:
                return False, "Not recording"
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            self.is_recording = False
            logger.info("Stopped video recording")
            return True, "Recording stopped"

    def take_screenshot(self):
        with self.lock:
            if self.current_frame is None:
                return False, "No frame available"
                
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_prefix = f"session_{self.session_id}_" if self.session_id else ""
            filename = os.path.join(config.SCREENSHOTS_DIR, f"screenshot_{session_prefix}{timestamp_str}.jpg")
            
            try:
                cv2.imwrite(filename, self.current_frame)
                if self.session_id:
                    self.db.update_session_metadata(self.session_id, screenshot_path=filename)
                return True, f"Saved as {filename}"
            except Exception as e:
                logger.error(f"Error saving screenshot: {e}")
                return False, f"Failed to save screenshot: {e}"

    def _process_loop(self):
        try:
            while self.is_running:
                if self.video_src is None:
                    break
                    
                ret, frame = self.video_src.read()
                if not ret:
                    logger.info("End of video stream or error reading frame.")
                    if hasattr(self, '_pending_stop_status'):
                        self._pending_stop_status = 'completed'
                    break

                self.frame_number += 1

                detections, inf_speed, raw_results = self.detector.detect(frame)
                tracks = self.tracker.update(detections, frame, raw_results)
                
                annotated_frame = self.visualizer.draw_annotations(frame.copy(), tracks)
                fps = self.fps_counter.update()
                annotated_frame = self.visualizer.draw_fps(annotated_frame, fps)
                annotated_frame = self.visualizer.draw_object_count(annotated_frame, len(tracks))
                annotated_frame = self.visualizer.draw_inference_speed(annotated_frame, inf_speed)
                
                db_detections = []
                
                with self.lock:
                    self.current_frame = annotated_frame
                    self.current_fps = fps
                    self.inference_time = inf_speed
                    self.tracked_count = len(tracks)
                    self.total_detections += len(detections)
                    
                    self.session_fps_samples += 1
                    self.session_total_fps += fps
                    
                    self.recent_objects = []
                    for t in tracks:
                        track_id = t.get("track_id", 0)
                        conf = float(t.get("confidence", 0.0)) * 100
                        obj_class = t.get("class_name", "Unknown")
                        
                        self.all_tracked_ids.add(track_id)
                        self.session_detection_count += 1
                        self.session_total_confidence += conf
                        
                        self.recent_objects.append({
                            "id": track_id,
                            "object": obj_class,
                            "confidence": round(conf, 2),
                            "status": "Tracking",
                            "time": datetime.now().strftime("%H:%M:%S")
                        })
                        
                        self._pending_db_detections.append({
                            'tracking_id': track_id,
                            'object_class': obj_class,
                            'confidence': round(conf, 2),
                            'frame_number': self.frame_number
                        })
                        
                    if self.is_recording and self.video_writer:
                        self.video_writer.write(annotated_frame)
                
                # Batch database writes every 30 frames to prevent blocking
                if self.session_id and len(self._pending_db_detections) >= 30:
                    batch_to_save = self._pending_db_detections.copy()
                    self._pending_db_detections.clear()
                    self.db.save_detections(self.session_id, batch_to_save)
                    
                time.sleep(0.01)
        except Exception as e:
            logger.error(f"Critical error in processing loop: {e}", exc_info=True)
            if hasattr(self, '_pending_stop_status'):
                self._pending_stop_status = 'failed'
        finally:
            self.is_running = False
            status = getattr(self, '_pending_stop_status', 'stopped')
            self._cleanup_stream(status=status)
