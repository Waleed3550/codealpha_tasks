import cv2
import sys
import config
from video.video_source import VideoSource
from detection.detector import ObjectDetector
from tracking.tracker import ObjectTracker
from visualization.visualizer import Visualizer
from utils.helpers import FPSCounter

def main():
    print("Starting Object Detection and Tracking System...")
    
    # Initialize components
    video_src = VideoSource(config.VIDEO_SOURCE)
    
    if not video_src.start():
        print(f"Error: Could not open video source {config.VIDEO_SOURCE}")
        print("Please check if your webcam is connected or if the video file path is correct.")
        sys.exit(1)
        
    print("Video source opened successfully.")
    
    # Setup optional video recording
    video_writer = None
    if getattr(config, 'SAVE_OUTPUT_VIDEO', False):
        width = int(video_src.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_src.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = getattr(config, 'OUTPUT_FPS', 30)
        # Fallback to source FPS if configured output FPS is 0 or invalid
        if fps <= 0:
            fps = int(video_src.cap.get(cv2.CAP_PROP_FPS))
            if fps <= 0: fps = 30
            
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        import time as ts
        default_out = os.path.join(config.RECORDINGS_DIR, f"desktop_record_{int(ts.time())}.mp4")
        video_writer = cv2.VideoWriter(default_out, fourcc, fps, (width, height))
        print(f"Video recording enabled. Saving to: {default_out}")
    
    # Load detector (Automatically downloads YOLO model on first run)
    detector = ObjectDetector(model_name=config.MODEL_NAME, device=config.DEVICE)
    tracker = ObjectTracker()
    visualizer = Visualizer()
    
    print("System initialized. Press 'q' in the video window to exit.")
    
    # Main processing loop
    fps_counter = FPSCounter()
    
    while True:
        ret, frame = video_src.read()
        if not ret:
            print("End of video stream or error reading frame.")
            break
            
        # 1. Object Detection
        detections, inference_speed, raw_results = detector.detect(frame)
        
        # 2. Object Tracking
        tracks = tracker.update(detections, frame, raw_results)
        
        # Calculate FPS
        fps = fps_counter.update()
        
        # 3. Visualization (Now uses tracks instead of raw detections)
        frame = visualizer.draw_annotations(frame, tracks)
        frame = visualizer.draw_fps(frame, fps)
        frame = visualizer.draw_object_count(frame, len(tracks))
        frame = visualizer.draw_inference_speed(frame, inference_speed)
        
        # Display the video
        cv2.imshow("Real Time Object Detection and Tracking System", frame)
        
        # Save output video if enabled
        if video_writer is not None:
            try:
                video_writer.write(frame)
            except Exception as e:
                print(f"Warning: Failed to write frame to video output. {e}")
        
        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            print("Exit requested by user.")
            break
        elif key == ord('s') or key == ord('S'):
            import time as ts
            filename = os.path.join(config.SCREENSHOTS_DIR, f"screenshot_{int(ts.time())}.png")
            cv2.imwrite(filename, frame)
            print(f"Screenshot saved to {filename}")
        elif key == ord('r') or key == ord('R'):
            if video_writer is None:
                # Start recording
                width = int(video_src.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(video_src.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps_out = getattr(config, 'OUTPUT_FPS', 30)
                if fps_out <= 0:
                    fps_out = int(video_src.cap.get(cv2.CAP_PROP_FPS))
                    if fps_out <= 0: fps_out = 30
                try:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    import time as ts
                    out_path = os.path.join(config.RECORDINGS_DIR, f"desktop_record_{int(ts.time())}.mp4")
                    video_writer = cv2.VideoWriter(out_path, fourcc, fps_out, (width, height))
                    print(f"Video recording STARTED. Saving to: {out_path}")
                except Exception as e:
                    print(f"Error initializing VideoWriter: {e}")
            else:
                # Stop recording safely
                video_writer.release()
                video_writer = None
                print("Video recording STOPPED.")
            
    # Cleanup resources properly
    video_src.release()
    if video_writer is not None:
        video_writer.release()
    cv2.destroyAllWindows()
    print("Application closed safely.")

if __name__ == "__main__":
    main()
