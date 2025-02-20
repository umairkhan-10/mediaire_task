import threading

from client import main as brain_report_client
from common.logger import logger
from server import main as brain_scan_server

if __name__ == "__main__":
    brain_report_client = brain_report_client()
    brain_scan_server = brain_scan_server()

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        # terminate gracefully
        brain_report_client.stop()
        brain_scan_server.stop()
        logger.info("FrHUB stopped successfully.")
