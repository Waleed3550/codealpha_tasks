import sqlite3
import os
import config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self._initialize_database()

    def _get_connection(self):
        conn = sqlite3.connect(config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON") # Enforce foreign key constraints
        return conn

    def _initialize_database(self):
        logger.info("Initializing SQLite database...")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_type TEXT,
                    source_name TEXT,
                    started_at DATETIME,
                    completed_at DATETIME,
                    status TEXT,
                    total_detections INTEGER DEFAULT 0,
                    total_tracked_objects INTEGER DEFAULT 0,
                    average_confidence REAL DEFAULT 0.0,
                    average_fps REAL DEFAULT 0.0,
                    processing_time REAL DEFAULT 0.0,
                    output_video TEXT,
                    screenshot_path TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    tracking_id INTEGER,
                    object_class TEXT,
                    confidence REAL,
                    frame_number INTEGER,
                    timestamp DATETIME,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            conn.commit()
        logger.info("Database initialized successfully.")

    def create_session(self, input_type, source_name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute('''
                INSERT INTO sessions (input_type, source_name, started_at, status)
                VALUES (?, ?, ?, ?)
            ''', (input_type, source_name, now, 'running'))
            conn.commit()
            return cursor.lastrowid

    def update_session_metadata(self, session_id, output_video=None, screenshot_path=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if output_video:
                cursor.execute('UPDATE sessions SET output_video = ? WHERE id = ?', (output_video, session_id))
            if screenshot_path:
                cursor.execute('UPDATE sessions SET screenshot_path = ? WHERE id = ?', (screenshot_path, session_id))
            conn.commit()

    def end_session(self, session_id, status, total_detections, total_tracked_objects, avg_confidence, avg_fps, processing_time):
        valid_statuses = ['completed', 'stopped', 'failed']
        if status not in valid_statuses:
            status = 'stopped'
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute('''
                UPDATE sessions 
                SET completed_at = ?, status = ?, total_detections = ?, 
                    total_tracked_objects = ?, average_confidence = ?, 
                    average_fps = ?, processing_time = ?
                WHERE id = ?
            ''', (now, status, total_detections, total_tracked_objects, avg_confidence, avg_fps, processing_time, session_id))
            conn.commit()

    def save_detections(self, session_id, detections_list):
        if not detections_list:
            return
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()
                records = [
                    (session_id, d.get('tracking_id', 0), d.get('object_class', 'Unknown'), float(d.get('confidence', 0.0)), int(d.get('frame_number', 0)), now)
                    for d in detections_list
                ]
                cursor.executemany('''
                    INSERT INTO detections (session_id, tracking_id, object_class, confidence, frame_number, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', records)
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving detections to DB: {e}")

    def get_all_sessions(self, limit=20, offset=0):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions ORDER BY started_at DESC LIMIT ? OFFSET ?', (limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def get_total_sessions_count(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM sessions')
            return cursor.fetchone()[0]

    def get_session_by_id(self, session_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            session = cursor.fetchone()
            if not session:
                return None
            
            cursor.execute('SELECT * FROM detections WHERE session_id = ? ORDER BY frame_number ASC', (session_id,))
            detections = [dict(row) for row in cursor.fetchall()]
            
            result = dict(session)
            result['detections'] = detections
            return result
            
    def delete_session(self, session_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Fetch session to get file paths before deleting
            cursor.execute('SELECT output_video, screenshot_path FROM sessions WHERE id = ?', (session_id,))
            session = cursor.fetchone()
            
            if session:
                out_vid = session['output_video']
                screenshot = session['screenshot_path']
                
                # Delete files safely if they belong to output directory
                if out_vid and os.path.exists(out_vid) and out_vid.startswith(config.OUTPUT_DIR):
                    try: os.remove(out_vid)
                    except: pass
                    
                if screenshot and os.path.exists(screenshot) and screenshot.startswith(config.OUTPUT_DIR):
                    try: os.remove(screenshot)
                    except: pass
            
            # Delete detections (Foreign key ON + ON DELETE CASCADE usually handles this, 
            # but we explicitly delete to be safe if schema was created before PRAGMA)
            cursor.execute('DELETE FROM detections WHERE session_id = ?', (session_id,))
            
            # Delete the session
            cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
            conn.commit()
            return True
