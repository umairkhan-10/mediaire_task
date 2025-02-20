import threading

from client import main as brain_scan_client
from common.logger import logger
from server import main as brain_report_server

if __name__ == "__main__":
    brain_scan_client = brain_scan_client()
    brain_report_server = brain_report_server()

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        # terminate gracefully
        brain_scan_client.stop()
        brain_report_server.stop()
        logger.info("FrPACS stopped successfully.")
