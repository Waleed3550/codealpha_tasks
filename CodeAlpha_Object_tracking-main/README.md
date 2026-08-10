# Intelligent Real-Time Object Tracking System

## Project Overview
This project is an advanced, real-time Computer Vision web application designed for seamless Object Detection and Tracking. It provides a highly interactive and professional dashboard to perform object tracking on live camera streams and uploaded videos.

---

## 1. Technology Stack
- **Backend Framework:** Python (Flask, Werkzeug)
- **Computer Vision:** Ultralytics YOLOv8, OpenCV (cv2)
- **Object Tracking:** ByteTrack
- **Database:** SQLite3
- **Frontend UI:** Vanilla HTML5, CSS3, JavaScript, FontAwesome, SweetAlert2

## 2. System Requirements
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python Version:** Python 3.8+ (Tested up to 3.11).
- **RAM:** Minimum 4GB (8GB+ recommended).
- **CPU/GPU:** A modern multi-core CPU is sufficient due to default Nano models, but an NVIDIA GPU (CUDA) is highly recommended for low-latency inference.

## 3. Project Architecture & Data Flow
This project follows a clear Client-Server architecture with a dedicated background worker for heavy AI processing.

### System Components
- **Frontend (Browser):** Built with HTML, CSS, and JavaScript. It provides the user interface (dashboard). It requests the video feed and continuously asks the server for the latest statistics (like FPS and tracking counts) without refreshing the page.
- **Flask Backend:** A Python web server that acts as the bridge. It receives commands from the frontend (like "Start Camera"), hosts the API routes, and streams the video back to the browser.
- **Processing Service:** The brain of the application. It runs on a separate background thread so it doesn't freeze the Flask server. It manages the entire computer vision loop.
- **OpenCV:** Captures the raw frames directly from the webcam or reads them from an uploaded video file.
- **YOLO (You Only Look Once):** The deep learning model that looks at the OpenCV frame and finds objects (like a person or car), drawing bounding boxes around them.
- **ByteTrack:** The tracking algorithm that assigns a unique ID (e.g., #1) to the object found by YOLO and follows it across multiple frames.
- **SQLite:** A lightweight database. Instead of saving heavy video files to the database, it only saves text data (metadata) like the session start time, the object IDs, and their confidence scores.

### How Data Moves (The Workflow)
1. The user clicks **Start** on the Frontend.
2. The **Flask Backend** receives the command and tells the **Processing Service** to wake up.
3. **OpenCV** starts grabbing pictures (frames) from the camera, one by one.
4. Each frame is sent to **YOLO**, which detects where the objects are.
5. The detections are passed to **ByteTrack**, which links them to previously seen objects to maintain a consistent ID.
6. The **Processing Service** draws these boxes and IDs onto the frame, sends the frame back to the **Frontend** to be displayed, and simultaneously saves the tracking data to **SQLite**.

## 4. Folder Structure
```text
Object_tracking/
├── app.py                      # Main Flask application and REST API definitions
├── config.py                   # Central configuration (Limits, thresholds, paths)
├── requirements.txt            # Python dependencies list
├── database.db                 # SQLite storage for session histories
├── detection/                  # YOLOv8 object detection module
├── tracking/                   # ByteTrack tracking algorithm implementation
├── video/                      # OpenCV video source capture managers
├── visualization/              # UI drawing for bounding boxes and metrics
├── services/                   
│   ├── database_service.py     # Database CRUD and History pagination
│   └── processing_service.py   # Multi-threaded CV pipeline orchestrator
├── templates/                  
│   └── index.html              # Frontend UI dashboard
├── static/                     
│   ├── css/style.css           # Custom stylesheets
│   └── js/app.js               # Reactive JS controllers
├── output/                     # Secured directory for generated outputs
│   ├── recordings/             # Annotated mp4 outputs
│   └── screenshots/            # Annotated jpeg screenshots
└── videos/                     
    └── uploads/                # Secured directory for uploaded user videos
```

## 5. Installation & Setup

### Virtual Environment Setup
Ensure you are using a virtual environment to prevent dependency conflicts. The following are exact Windows commands:
```powershell
python -m venv venv
venv\Scripts\activate
```

### Dependency Installation
With the virtual environment active, install the required packages:
```powershell
python -m pip install -r requirements.txt
```

### Database Initialization
The SQLite database (`database.db`) is automatically initialized the first time you run the application. The system will create the necessary `sessions` and `detections` tables with Foreign Key constraints enabled for integrity.

## 6. How to Start the Application
To start the Flask backend:
```bash
python app.py
```
*Note: Ensure the virtual environment is active before running this command.*

## 7. How to Open the Website
Once the backend is running, open your web browser (Chrome/Edge/Firefox) and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 8. Application Workflows & Features

### Camera Workflow
Select the **Camera Input** tab on the dashboard. Click **START CAMERA**. The system will attempt to connect to your primary webcam (Camera Index 0 by default, adjustable in Settings). Once connected, the MJPEG feed will appear, and real-time bounding boxes will overlay detected objects. Click **STOP CAMERA** to safely release the hardware.

### Video Upload Workflow
Select the **Video Upload** tab. Drag and drop or select an MP4, AVI, MOV, or MKV file. A secure size limit of 100MB is enforced. Click **START PROCESSING** to begin analyzing the video frame-by-frame. The video will be processed by the CV pipeline exactly like a live stream.

### YOLO Explanation
**You Only Look Once (YOLO)** is a state-of-the-art, real-time object detection algorithm. This project uses **YOLOv8** (specifically `yolov8n.pt` for CPU efficiency). It analyzes an image in a single pass to predict bounding boxes and class probabilities simultaneously, making it incredibly fast.

### ByteTrack Explanation
**ByteTrack** is a highly efficient tracking algorithm. Unlike standard trackers that throw away low-confidence detections, ByteTrack associates almost every detection box by considering similarities in motion and appearance. This allows it to maintain persistent **Tracking IDs** even when an object becomes partially occluded or drops in confidence temporarily.

### SQLite Explanation
The project uses SQLite as a serverless database to permanently log sessions without clogging disk storage with massive frame data. 
- The `sessions` table tracks metadata (Start/End times, Average FPS, Total Detections, Output File paths). 
- The `detections` table saves detailed information per tracked object (Class, Confidence, Frame Number) linked via Foreign Keys.

### Screenshot Workflow
While a stream or video is processing, clicking **Screenshot** immediately grabs the current *annotated* frame. The image is saved to `output/screenshots/` with a unique timestamp. You can download this directly from the session's History modal.

### Recording Workflow
Clicking **Start Recording** initializes an OpenCV `VideoWriter`. Every subsequent annotated frame is pushed to an `.mp4` file in `output/recordings/` at 30 FPS. Clicking **Stop Recording** securely finalizes and saves the file, which can then be downloaded from the History pane.

### History Workflow
The **Sessions View** dynamically paginates all processed inputs. Clicking a session opens a detailed modal showing Class Distributions, processing duration, and a tabular list of every detection instance. If a Screenshot or Recording was made during that session, secure download buttons will appear here.

### Settings
The **Settings** view allows real-time configuration of the application without restarting the server:
- **Camera Source Index:** Change from default `0` if using external webcams.
- **YOLO Model:** Switch between Nano (Fastest) and Small models.
- **Confidence Threshold:** A slider to filter out weak detections (0.1 - 1.0).
- **Image Size:** Switch between 320px (faster) and 640px (higher accuracy).
- **Device:** Switch between CPU, CUDA (GPU), and MPS (Apple Silicon).

---

## 9. API Overview
The backend exposes a clean REST API:
- `GET /` - Renders the dashboard UI.
- `GET /api/status` - Returns live telemetry (FPS, Tracker state, System connections).
- `GET /api/sessions?page=1&limit=15` - Returns paginated session metadata.
- `GET /api/session/<id>` - Returns a specific session's metadata and object detections.
- `DELETE /api/session/<id>` - Clears session DB records and securely wipes associated files.
- `GET /api/detections` - Returns currently tracked objects for live display.
- `POST /api/start-camera` - Initializes webcam processing.
- `POST /api/stop-camera` - Cleans up resources.
- `POST /api/upload-video` - Handles strict format & size validations before saving files to `videos/uploads/`.
- `POST /api/start-processing` - Starts YOLO/ByteTrack on a specific uploaded file.
- `POST /api/stop-processing` - Stops video processing.
- `POST /api/screenshot` - Captures an annotated frame to disk.
- `POST /api/start-recording` / `POST /api/stop-recording` - Manages live annotated video writing.
- `GET /api/settings` / `POST /api/settings` - Fetches or applies CV configuration securely.
- `GET /video-feed` - Yields the live MJPEG stream.

---

## 10. Troubleshooting

- **Camera Unavailable:** Ensure no other application (like Zoom or Skype) is currently using the webcam. Try changing the Camera Source Index in Settings to `1` or `2`.
- **Sluggish Performance:** The application defaults to CPU-friendly settings (`320px` image size, Nano model). If performance is poor, ensure your laptop is plugged into power, close heavy background apps, and verify `IMAGE_SIZE` is not set to `640px` unless you have a dedicated GPU.
- **File Upload Error:** Ensure your video is under 100MB and is one of the supported formats (MP4, AVI, MOV, MKV).
- **Database Locked:** If the dashboard statistics freeze, restart the Flask server. SQLite occasionally locks if too many concurrent reads/writes happen (though batching is implemented to mitigate this).

## 11. Known Limitations
- Modifying configurations (like YOLO model or Device) in Settings requires starting a *new* session (Camera or Video) for the changes to take effect natively.
- ByteTrack IDs are sequential per stream instance. When a stream is stopped and restarted, tracking IDs will reset back to 1.
- The web browser's caching might occasionally cache MJPEG feeds improperly on hard refresh, simply click Stop and Start Camera again.

## 12. Future Improvements
- **Multi-Camera Support:** Extend the dashboard to display feeds from multiple IP cameras or USB webcams simultaneously.
- **Export to CSV/Excel:** Add functionality to export the session's detection history directly to a CSV or Excel file for deeper analytical review.
- **Region of Interest (ROI):** Allow users to draw polygons on the video feed to only detect/track objects entering specific zones (e.g., restricted area monitoring).
- **User Authentication:** Introduce a login system to restrict access to the dashboard and separate history by user accounts.
- **Docker Integration:** Containerize the application to completely eliminate local environment inconsistencies.
