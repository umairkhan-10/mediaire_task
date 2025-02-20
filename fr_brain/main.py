import threading

from common.logger import logger
from fr_brain.processor import FrBRAINScanProcessor

if __name__ == "__main__":
    brain_scan_processor_instance = FrBRAINScanProcessor()
    processor_thread = threading.Thread(target=brain_scan_processor_instance.process_brain_scans)
    processor_thread.start()
    try:
        while True:
            # Main thread waits here allowing the processing thread to run
            threading.Event().wait(1)
    except KeyboardInterrupt:
        # Terminate gracefully
        brain_scan_processor_instance.stop()
        # wait for processes
        processor_thread.join()
        logger.info("FrBRAIN stopped successfully.")
