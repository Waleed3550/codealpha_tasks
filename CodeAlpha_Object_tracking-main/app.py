import os
import cv2
import time
import logging
from flask import Flask, render_template, Response, request, jsonify
from werkzeug.utils import secure_filename

import config
from services.processing_service import ProcessingService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

pipeline = ProcessingService()
logger.info("Application starting up, initializing backend pipeline.")

# ----------------------------------------------------
#  FRONTEND ROUTES
# ----------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video-feed')
def video_feed():
    def gen_frames():
        while True:
            with pipeline.lock:
                frame = pipeline.current_frame
            
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.03) # Cap to ~33fps and prevent lock starvation
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ----------------------------------------------------
#  API ROUTES
# ----------------------------------------------------

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"success": False, "message": "An internal server error occurred."}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    with pipeline.lock:
        avg_conf = (pipeline.session_total_confidence / pipeline.session_detection_count) if pipeline.session_detection_count > 0 else 0
        proc_time = (time.time() - pipeline.session_start_time) if pipeline.session_start_time else 0
        
        input_type_val = None
        if pipeline.video_src:
            input_type_val = "camera" if isinstance(pipeline.video_src.source, int) else "video"
            
        return jsonify({
            "camera_status": pipeline.is_running and input_type_val == "camera",
            "processing_status": pipeline.is_running and input_type_val == "video",
            "yolo_status": pipeline.detector is not None,
            "tracker_status": pipeline.tracker is not None,
            "recording_status": pipeline.is_recording,
            "current_session_id": pipeline.session_id if pipeline.is_running else None,
            "fps": round(pipeline.current_fps, 1) if pipeline.is_running and pipeline.current_fps else 0,
            "tracked_objects": pipeline.tracked_count if pipeline.is_running else 0,
            "inference_time": round(pipeline.inference_time, 1) if pipeline.is_running else 0,
            "total_detections": pipeline.total_detections if pipeline.is_running else 0,
            "average_confidence": round(avg_conf, 1) if pipeline.is_running else 0,
            "processing_time": round(proc_time, 1) if pipeline.is_running else 0,
            "input_type": input_type_val if pipeline.is_running else None,
            # Keeping these for backwards compatibility with our frontend JS mapping
            "current_session": pipeline.session_id,
            "avg_confidence": round(avg_conf, 1) if pipeline.is_running else 0,
            "current_input": input_type_val if pipeline.is_running else None,
            "recent_objects": pipeline.recent_objects
        })

@app.route('/api/detections', methods=['GET'])
def api_detections():
    with pipeline.lock:
        if not pipeline.is_running:
            return jsonify([])
            
        # Convert our recent_objects schema to the specific requirement for this step
        mapped_detections = []
        for obj in pipeline.recent_objects:
            mapped_detections.append({
                "tracking_id": obj["id"],
                "class_id": 0, # Placeholder if class_id isn't directly in recent_objects currently
                "class_name": obj["object"],
                "confidence": obj["confidence"] / 100.0 if "confidence" in obj else 0.0,
                "status": obj.get("status", "tracking")
            })
        return jsonify(mapped_detections)

@app.route('/api/sessions', methods=['GET'])
def api_sessions():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = (page - 1) * limit
        
        sessions = pipeline.db.get_all_sessions(limit=limit, offset=offset)
        total = pipeline.db.get_total_sessions_count()
        
        return jsonify({
            "success": True, 
            "data": sessions,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit if total > 0 else 1
            }
        })
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return jsonify({"success": False, "message": "Failed to fetch sessions"}), 500

@app.route('/api/session/<int:session_id>', methods=['GET'])
def api_session(session_id):
    try:
        session = pipeline.db.get_session_by_id(session_id)
        if not session:
            return jsonify({"success": False, "message": "Session not found"}), 404
        return jsonify({"success": True, "data": session})
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        return jsonify({"success": False, "message": "Failed to fetch session data"}), 500

from flask import send_file
import os

@app.route('/api/session/<int:session_id>/output', methods=['GET'])
def download_session_output(session_id):
    try:
        session = pipeline.db.get_session_by_id(session_id)
        if not session or not session.get('output_video'):
            return jsonify({"success": False, "message": "Output video not found"}), 404
            
        filepath = session['output_video']
        if not os.path.exists(filepath):
            return jsonify({"success": False, "message": "File no longer exists on server"}), 404
            
        # Security check to ensure it's in the allowed directory
        if not filepath.startswith(config.OUTPUT_DIR):
             return jsonify({"success": False, "message": "Access denied"}), 403
             
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading output for session {session_id}: {e}")
        return jsonify({"success": False, "message": "Download failed"}), 500

@app.route('/api/session/<int:session_id>/screenshot', methods=['GET'])
def download_session_screenshot(session_id):
    try:
        session = pipeline.db.get_session_by_id(session_id)
        if not session or not session.get('screenshot_path'):
            return jsonify({"success": False, "message": "Screenshot not found"}), 404
            
        filepath = session['screenshot_path']
        if not os.path.exists(filepath):
            return jsonify({"success": False, "message": "File no longer exists on server"}), 404
            
        # Security check to ensure it's in the allowed directory
        if not filepath.startswith(config.OUTPUT_DIR):
             return jsonify({"success": False, "message": "Access denied"}), 403
             
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading screenshot for session {session_id}: {e}")
        return jsonify({"success": False, "message": "Download failed"}), 500

@app.route('/api/session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        success = pipeline.db.delete_session(session_id)
        if success:
            return jsonify({"success": True, "message": "Session deleted successfully"})
        else:
            return jsonify({"success": False, "message": "Session not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return jsonify({"success": False, "message": "Failed to delete session"}), 500

@app.route('/api/start-camera', methods=['POST'])
def api_start_camera():
    data = request.get_json(silent=True) or {}
    cam_index = data.get('source', config.VIDEO_SOURCE)
    
    # Try parsing as integer for camera index if it looks like one
    try:
        cam_index = int(cam_index)
    except ValueError:
        pass
        
    success, msg = pipeline.start_stream(source=cam_index)
    return jsonify({"success": success, "message": msg})

@app.route('/api/stop-camera', methods=['POST'])
def api_stop_camera():
    success, msg = pipeline.stop_stream()
    return jsonify({"success": success, "message": msg})

def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in config.VIDEO_EXTENSIONS

@app.route('/api/upload-video', methods=['POST'])
def api_upload_video():
    if 'video' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    file = request.files['video']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            logger.info(f"Video uploaded successfully to {filepath}")
            return jsonify({"success": True, "message": "Uploaded successfully", "filepath": filepath})
        except Exception as e:
            logger.error(f"Error saving uploaded video: {e}")
            return jsonify({"success": False, "message": "Failed to save video on server"}), 500
    else:
        return jsonify({"success": False, "message": f"Invalid file format. Allowed: {config.VIDEO_EXTENSIONS}"}), 400

@app.route('/api/start-processing', methods=['POST'])
def api_start_processing():
    data = request.get_json(silent=True) or {}
    filepath = data.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({"success": False, "message": "Invalid or missing video file path"})
    
    # Security check: Ensure filepath is within our allowed directories
    abspath = os.path.abspath(filepath)
    if not abspath.startswith(os.path.abspath(config.BASE_DIR)):
         return jsonify({"success": False, "message": "Unauthorized file path"}), 403
         
    success, msg = pipeline.start_stream(source=filepath)
    return jsonify({"success": success, "message": msg})

@app.route('/api/stop-processing', methods=['POST'])
def api_stop_processing():
    success, msg = pipeline.stop_stream()
    return jsonify({"success": success, "message": msg})

@app.route('/api/screenshot', methods=['POST'])
def api_screenshot():
    success, msg = pipeline.take_screenshot()
    return jsonify({"success": success, "message": msg})

@app.route('/api/start-recording', methods=['POST'])
def api_start_recording():
    success, msg = pipeline.start_recording()
    return jsonify({"success": success, "message": msg})

@app.route('/api/stop-recording', methods=['POST'])
def api_stop_recording():
    success, msg = pipeline.stop_recording()
    return jsonify({"success": success, "message": msg})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify({
        "success": True,
        "data": {
            "model_name": getattr(config, 'MODEL_NAME', 'yolov8n.pt'),
            "confidence_threshold": getattr(config, 'CONFIDENCE_THRESHOLD', 0.25),
            "image_size": getattr(config, 'IMAGE_SIZE', 320),
            "device": getattr(config, 'DEVICE', 'cpu'),
            "video_source": getattr(config, 'VIDEO_SOURCE', 0)
        }
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        data = request.get_json(silent=True) or {}
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
            
        # Validate and apply Confidence Threshold
        if 'confidence_threshold' in data:
            val = float(data['confidence_threshold'])
            if 0.0 <= val <= 1.0:
                config.CONFIDENCE_THRESHOLD = val
                
        # Validate and apply Image Size
        if 'image_size' in data:
            val = int(data['image_size'])
            if val > 0:
                config.IMAGE_SIZE = val
                
        # Validate and apply Device
        if 'device' in data:
            val = str(data['device']).lower()
            if val in ['cpu', 'cuda', 'mps']:
                config.DEVICE = val
                
        # Validate and apply Camera Source
        if 'video_source' in data:
            val = data['video_source']
            try:
                val = int(val)
            except ValueError:
                val = str(val)
            config.VIDEO_SOURCE = val
            
        # Flag re-init for next stream if model params changed
        if any(k in data for k in ['confidence_threshold', 'image_size', 'device']):
            with pipeline.lock:
                pipeline.detector = None
                pipeline.tracker = None
            
        return jsonify({"success": True, "message": "Settings updated successfully"})
    except ValueError as e:
        return jsonify({"success": False, "message": "Invalid value format provided"}), 400
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({"success": False, "message": "Failed to update settings"}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask backend at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.DEBUG_MODE, threaded=True)
