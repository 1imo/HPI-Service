import sqlite3
import os
import inspect
import datetime
import traceback
from threading import Lock
from pathlib import Path
import sys

class Logger:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.db_path = Path(__file__).parent / 'logs.db'
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    file TEXT,
                    line_number INTEGER,
                    method_name TEXT,
                    message TEXT
                )
            ''')
            conn.commit()
            conn.close()

    def write(self, message, is_exception=False):
        timestamp = datetime.datetime.now().isoformat()
        
        if is_exception:
            # Get the full traceback
            tb = traceback.extract_tb(sys.exc_info()[2])
            # Get the last frame (where the error actually occurred)
            last_frame = tb[-1]
            file_path = last_frame.filename
            line_number = last_frame.lineno
            method_name = last_frame.name
        else:
            frame = inspect.currentframe().f_back
            file_path = frame.f_code.co_filename
            line_number = frame.f_lineno
            method_name = frame.f_code.co_name

        log_entry = f"[{timestamp}] {file_path}:{line_number} in {method_name}: {message}"

        if is_exception:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO logs (timestamp, file, line_number, method_name, message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, file_path, line_number, method_name, message))
        else:
            print(log_entry)

    def read_all(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs')
            return cursor.fetchall()

# Global instance
logger = Logger()

def simulate_function():
    try:
        # Simulating some operations
        result = 10 / 0  # This will raise a ZeroDivisionError
    except Exception as e:
        logger.write(f"An error occurred: {str(e)}", is_exception=True)
        raise  # Re-raise the exception after logging

def test_logger():
    logger.write("Starting the test")
    
    try:
        simulate_function()
    except Exception as e:
        logger.write(f"Caught an exception: {str(e)}")
    
    logger.write("Test completed")
    
    print("\nExceptions logged to database:")
    all_logs = logger.read_all()
    for log in all_logs:
        print(log)

if __name__ == '__main__':
    test_logger()
