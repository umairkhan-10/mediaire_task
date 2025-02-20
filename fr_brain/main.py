import threading

from common.logger import logger
from processor import main as brain_scan_processor

if __name__ == "__main__":
    brain_scan_processor_instance = brain_scan_processor()
    try:
        while True:
            # main thread waits here allow processing thread to run
            threading.Event().wait(1)
    except KeyboardInterrupt:
        # terminate gracefully
        brain_scan_processor_instance.stop()
        logger.info("FrBRAIN stopped successfully.")
