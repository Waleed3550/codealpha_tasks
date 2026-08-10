"""
Configuration settings for the Object Detection and Tracking System.
"""
import os

# Base# Directory Structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
VIDEOS_DIR = os.path.join(BASE_DIR, 'videos')
UPLOAD_FOLDER = os.path.join(VIDEOS_DIR, 'uploads')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, 'screenshots')
RECORDINGS_DIR = os.path.join(OUTPUT_DIR, 'recordings')
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

# Ensure directories exist
for d in [MODELS_DIR, VIDEOS_DIR, UPLOAD_FOLDER, OUTPUT_DIR, SCREENSHOTS_DIR, RECORDINGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ----------------- #
#   CONFIGURATION   #
# ----------------- #

# Flask Configuration
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
DEBUG_MODE = True
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}
MAX_UPLOAD_SIZE_MB = 100
MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Enforce at Flask level

# Video Source: Use 0 for primary webcam, or provide a path string for a local video file.
VIDEO_SOURCE = 0

# YOLO Model Settings
MODEL_NAME = "yolov8n.pt"  
CONFIDENCE_THRESHOLD = 0.25
IMAGE_SIZE = 320
DEVICE = "cpu"  # Force CPU usage as requested

# Output Settings
SAVE_OUTPUT_VIDEO = False
OUTPUT_VIDEO_PATH = os.path.join(OUTPUT_DIR, "output.mp4")
OUTPUT_FPS = 30

# Tracker Configuration
TRACKER_TYPE = "bytetrack"
TRACKER_TRACK_HIGH_THRESH = 0.5
TRACKER_TRACK_LOW_THRESH = 0.1
TRACKER_NEW_TRACK_THRESH = 0.6
TRACKER_TRACK_BUFFER = 30
TRACKER_MATCH_THRESHOLD = 0.8
TRACKER_FRAME_RATE = 30
