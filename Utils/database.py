import json
import fcntl
from pathlib import Path
from datetime import datetime
import threading
import tempfile
import io
import sys
import signal
import os
import time

class Database:
    def __init__(self):
        self.file_path = Path(__file__).parent / "db.json"
        self.index = {}
        self.lock = threading.Lock()
        self._load_index()

    def _load_index(self):
        self.index.clear()
        if self.file_path.exists():
            with self.file_path.open('r') as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                offset = 0
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        vrm = list(record.keys())[0]
                        self.index[vrm] = offset
                        offset += len(line)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON: {line}")
                fcntl.flock(f, fcntl.LOCK_UN)

    def write(self, vrm, value):
        with self.lock:
            current_time = datetime.now().isoformat()

            def remove_rfr_comments(data):
                if isinstance(data, dict):
                    data.pop('rfrAndComments', None)
                    data.pop('basicDetails_imageUrl', None)
                    for key, val in data.items():
                        data[key] = remove_rfr_comments(val)
                elif isinstance(data, list):
                    return [remove_rfr_comments(item) for item in data]
                return data

            # Remove 'rfrAndComments' recursively from the input value
            value = remove_rfr_comments(value)

            if vrm not in self.index:
                new_value = {
                    key: [{
                        'value': val,
                        'created_at': current_time
                    }] if not isinstance(val, list) else val
                    for key, val in value.items()
                }
                new_value['created_at'] = current_time
                new_value['updated_at'] = current_time
                new_value.setdefault('searched', [])
            else:
                existing_record = self._read_record_without_update(vrm)
                new_value = existing_record.copy()
                for key, val in value.items():
                    if key not in new_value:
                        new_value[key] = []
                    if not new_value[key] or new_value[key][-1]['value'] != val:
                        new_value[key].append({
                            'value': val,
                            'created_at': current_time
                        })
                new_value['updated_at'] = current_time

            with self.file_path.open('r+') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                content = f.read()
                records = [json.loads(line) for line in content.splitlines() if line.strip()]
                updated_records = [record for record in records if list(record.keys())[0] != vrm]
                updated_records.append({vrm: new_value})
                
                f.seek(0)
                for record in updated_records:
                    json.dump(record, f)
                    f.write('\n')
                f.truncate()
                fcntl.flock(f, fcntl.LOCK_UN)

            self._load_index()

    def readReg(self, vrm):
        with self.lock:
            if vrm in self.index:
                with self.file_path.open('r') as f:
                    fcntl.flock(f, fcntl.LOCK_SH)
                    f.seek(self.index[vrm])
                    line = f.readline().strip()
                    fcntl.flock(f, fcntl.LOCK_UN)
                    try:
                        record = json.loads(line)
                        data = record[vrm]
                        return data
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON for VRM: {vrm}")
                        print(f"Line content: {line}")
                        self._remove_corrupted_record(vrm)
                        return None
            else:
                return None

    def _read_record_without_update(self, vrm):
        with self.file_path.open('r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            f.seek(self.index[vrm])
            line = f.readline().strip()
            fcntl.flock(f, fcntl.LOCK_UN)
            record = json.loads(line)
            return record[vrm]

    def delete(self, vrm):
        with self.lock:
            if vrm in self.index:
                with self.file_path.open('r+') as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    content = f.read()
                    records = [json.loads(line) for line in content.splitlines() if line.strip()]
                    updated_records = [record for record in records if list(record.keys())[0] != vrm]
                    
                    f.seek(0)
                    for record in updated_records:
                        json.dump(record, f)
                        f.write('\n')
                    f.truncate()
                    fcntl.flock(f, fcntl.LOCK_UN)

                self._load_index()

    def _remove_corrupted_record(self, vrm):
        self.delete(vrm)

def test_database():
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        db = Database(temp_file.name)

        try:
            print("1. Basic Write and Read Test")
            db.write('ABC123', {'owner': 'John Doe', 'model': 'Toyota'})
            db.write('XYZ789', {'owner': 'Jane Smith', 'model': 'Honda'})
            print(db.readReg('ABC123'))
            print(db.readReg('XYZ789'))
            print(db.readReg('NONEXISTENT'))

            print("\n2. Update Existing Record Test")
            db.write('ABC123', {'color': 'Red'})
            print(db.readReg('ABC123'))

            print("\n3. Searched Attribute Test")
            for i in range(3):
                record = db.readReg('ABC123')
                if record and 'searched' in record:
                    searched_count = len(record['searched'])
                    print(f"ABC123 searched count: {searched_count}")
                    if searched_count > 0:
                        print(f"Last search timestamp: {record['searched'][-1]['created_at']}")
                    else:
                        print("No searches recorded yet")
                else:
                    print("Error: Unable to read search count for ABC123")

                # Simulate a search by updating the 'searched' attribute
                if record:
                    current_time = datetime.now().isoformat()
                    if 'searched' not in record:
                        record['searched'] = []
                    record['searched'].append({
                        'value': len(record['searched']) + 1,
                        'created_at': current_time
                    })
                    db.write('ABC123', record)

            print("\n4. Delete Record Test")
            db.write('DEL111', {'note': 'To be deleted'})
            print("Before deletion:", db.readReg('DEL111'))
            db.delete('DEL111')
            print("After deletion:", db.readReg('DEL111'))

            print("\n5. Database state after all operations:")
            db._load_index()
            print(f"Records in database: {list(db.index.keys())}")

        except Exception as e:
            print(f"An error occurred during testing: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            # Clean up the temporary file
            Path(temp_file.name).unlink()

if __name__ == "__main__":
    def timeout_handler(signum, frame):
        print("Script execution timed out.")
        sys.exit(1)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # Set a 30-second timeout

    try:
        test_database()
        print("Script execution completed.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        signal.alarm(0)  # Cancel the alarm