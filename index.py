import time
import json
import argparse
import signal
import sys
import os
import mmap
from multiprocessing import Process
from collections import deque

from interface import VehicleDataInterface, get_mot_history
from Utils.database import Database
from Utils.logging import logger

PID_FILE = '/tmp/vehicle_data_service.pid'
SHM_FILE = '/tmp/vehicle_data_service_queue.shm'
SHM_SIZE = 1024 * 10

class VehicleDataService:
    def __init__(self):
        try:
            self.interface = VehicleDataInterface(Database())
            self.running = False
            self.shm_file = open(SHM_FILE, 'r+b')
            self.shm = mmap.mmap(self.shm_file.fileno(), SHM_SIZE)
            self.queue = deque()
        except Exception as e:
            logger.write(f"Error in VehicleDataService.__init__: {str(e)}", is_exception=True)

    def __del__(self):
        try:
            self.shm.close()
            self.shm_file.close()
        except Exception as e:
            logger.write(f"Error in VehicleDataService.__del__: {str(e)}", is_exception=True)

    def get_vehicle_data(self, vrm):
        try:
            return self.interface.get_vehicle_data(vrm)
        except Exception as e:
            logger.write(f"Error in get_vehicle_data for VRM {vrm}: {str(e)}", is_exception=True)
            return None

    def start(self):
        try:
            self.running = True
            signal.signal(signal.SIGUSR1, self.handle_signal)
            while self.running:
                time.sleep(0.1)
        except Exception as e:
            logger.write(f"Error in start: {str(e)}", is_exception=True)

    def stop(self):
        try:
            self.running = False
        except Exception as e:
            logger.write(f"Error in stop: {str(e)}", is_exception=True)

    def handle_signal(self, signum, frame):
        try:
            self.process_queue()
        except Exception as e:
            logger.write(f"Error in handle_signal: {str(e)}", is_exception=True)

    def process_queue(self):
        try:
            self.shm.seek(0)
            queue_data = self.shm.read().decode().strip('\0')
            if queue_data:
                vrm = queue_data
                self.clear_shared_memory()
                if vrm:
                    self.process_vrm(vrm)
        except Exception as e:
            logger.write(f"Error in process_queue: {str(e)}", is_exception=True)

    def clear_shared_memory(self):
        try:
            self.shm.seek(0)
            self.shm.write(b'\0' * SHM_SIZE)
        except Exception as e:
            logger.write(f"Error in clear_shared_memory: {str(e)}", is_exception=True)

    def process_vrm(self, vrm):
        try:
            result = self.process_single_vrm(vrm)
            self.save_result(result)
        except Exception as e:
            logger.write(f"Error processing VRM {vrm}: {str(e)}", is_exception=True)

    def process_single_vrm(self, vrm):
        try:
            vehicle_data = self.get_vehicle_data(vrm)
            if vehicle_data is None:
                raise ValueError(f"No data found for VRM: {vrm}")
            
            # The get_vehicle_data method now returns the complete result including AI analysis
            result = f"VRM: {vrm}\n{vehicle_data}"
            
            # Write the result to the shared memory
            self.save_result(result)
            
            return result
        except Exception as e:
            logger.error(f"Error in process_single_vrm for {vrm}: {str(e)}")
            raise

    def save_result(self, result):
        try:
            self.shm.seek(0)
            encoded_result = result.encode('utf-8')
            if len(encoded_result) > SHM_SIZE:
                encoded_result = encoded_result[:SHM_SIZE]
            self.shm.write(encoded_result)
            self.shm.write(b'\0' * (SHM_SIZE - len(encoded_result)))  # Pad with null bytes
        except Exception as e:
            logger.write(f"Error in save_result: {str(e)}", is_exception=True)

def is_service_running():
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
        return False
    except Exception as e:
        logger.write(f"Error in is_service_running: {str(e)}", is_exception=True)
        return False

def run_service():
    try:
        service = VehicleDataService()
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        service.start()
        os.remove(PID_FILE)
    except Exception as e:
        logger.write(f"Error in run_service: {str(e)}", is_exception=True)

def send_command_to_service(command, vrm=None):
    try:
        if command == 'stop':
            os.kill(int(open(PID_FILE, 'r').read().strip()), signal.SIGTERM)
        elif command == 'add_vrm':
            with open(SHM_FILE, 'r+b') as f:
                shm = mmap.mmap(f.fileno(), SHM_SIZE)
                new_data = vrm.encode()
                
                if len(new_data) > SHM_SIZE:
                    new_data = new_data[:SHM_SIZE]
                
                shm.seek(0)
                shm.write(b'\0' * SHM_SIZE)
                shm.seek(0)
                shm.write(new_data)
                shm.close()
            
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGUSR1)
    except Exception as e:
        logger.write(f"Error in send_command_to_service: {str(e)}", is_exception=True)

def get_result(vrm):
    try:
        if os.path.exists(RESULT_FILE):
            with open(RESULT_FILE, 'r') as f:
                result = json.load(f)
                if vrm in result:
                    return result[vrm]
        return None
    except Exception as e:
        logger.write(f"Error in get_result for VRM {vrm}: {str(e)}", is_exception=True)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vehicle Data Service")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--stop", action="store_true", help="Stop the service")
    parser.add_argument("--vrm", help="Process a single VRM")
    args = parser.parse_args()

    def start_service():
        if not is_service_running():
            with open(SHM_FILE, 'wb') as f:
                f.write(b'\0' * SHM_SIZE)
            process = Process(target=run_service)
            process.start()
            time.sleep(2)
            print("Service started successfully.")
        else:
            print("Service is already running.")

    try:
        if args.start:
            start_service()
        elif args.stop:
            if is_service_running():
                send_command_to_service('stop')
                try:
                    os.remove(SHM_FILE)
                except FileNotFoundError:
                    pass
                print("Service stopped successfully.")
            else:
                print("Service is not running.")
        elif args.vrm:
            start_service()  # This will start the service only if it's not already running

            send_command_to_service('add_vrm', args.vrm)

            max_wait = 360  # 6 minutes
            result = None
            for i in range(max_wait):
                with open(SHM_FILE, 'r+b') as f:
                    shm = mmap.mmap(f.fileno(), SHM_SIZE)
                    result = shm.read().decode('utf-8').strip('\0')
                    shm.close()
                if result:
                    break
                time.sleep(1)

            if not result:
                error_message = f"Timeout waiting for result for VRM {args.vrm}"
                logger.error(error_message)
                print(json.dumps({"error": error_message}))
            else:
                print(json.dumps({"result": result}))
            
            # Clear the shared memory after reading the result
            with open(SHM_FILE, 'r+b') as f:
                shm = mmap.mmap(f.fileno(), SHM_SIZE)
                shm.seek(0)
                shm.write(b'\0' * SHM_SIZE)
                shm.close()

        else:
            parser.print_help()

        # This part will only run if --start was used
        if args.start:
            try:
                while is_service_running():
                    time.sleep(1)
            except KeyboardInterrupt:
                send_command_to_service('stop')
                print("Service stopped by user.")

    except Exception as e:
        logger.write(f"Error in main execution: {str(e)}", is_exception=True)
        print(json.dumps({"error": str(e)}))
    finally:
        if args.stop and os.path.exists(SHM_FILE):
            os.remove(SHM_FILE)