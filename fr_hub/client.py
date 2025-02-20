import json
import socket
import threading
import time

from common.config import BRAIN_REPORT_PORT, BRAIN_REPORT_HOST
from common.logger import logger
from common.utils import fetch_brain_report


class FrHUBBrainReportClient:
    """Sends brain reports to FrPACS

    Requirement:
        - FrHUB should persist brain scans so they can be processed later by FrBRAIN so we'll use some persistent storage to store the brain scan.
        - In case FrHUB is stopped and restarted, it must fetch pending brain reports from persistent storage and send it to FrPACS
        - If FrPACS stops, some brain reports will be failed to be sent to FrPACS, which is fine
           There is no need to retry or persistent storage required here for these failures, we'll just log them.
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.client_socket = None
        self.running_status = True

    def send_brain_report(self) -> None:
        """
        Sends brain reports to FrPACS.
        :return:
        """
        try:
            while self.running_status:
                try:
                    if not self.client_socket:
                        self.client_socket = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM
                        )
                        self.client_socket.connect((self.host, self.port))
                # In this case, report generated below will not be sent to FrPACS as FrPACS isn't running but that's Ok as per requirement.
                except Exception as e:
                    logger.error(f"FrPACS is not available to receive reports: {e}")

                # Fetch stored brain reports from DB and send it to FrPACS via socket
                # failed cases would be logged only as per requriemenet.
                # also it's fetching single report at a time which increases our DB call.
                # In an actual environment, we can also optimize it by fetching in batches to reduce DB calls
                report = fetch_brain_report()
                if report:
                    # Convert datetime object to string for JSON serialization
                    report["report_datetime"] = report["report_datetime"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    logger.info(f"Sending brain report to FrPACS: {report}")

                    try:
                        report_data = json.dumps(report)
                        self.client_socket.sendall(report_data.encode("utf-8"))
                        # receiving acknowledgment from FrPACS
                        response = self.client_socket.recv(1024).decode("utf-8")
                        logger.info(
                            f"Received an acknowledgment from FrPACS: {response}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to send brain report: {e}")
                        logger.error(f"Report not sent: {report}")
                        self.close_socket()
                else:
                    logger.info("No pending reports to process. Waiting for report...")
                    # sleep for 5 seconds before checking again as there is no report to send
                    time.sleep(5)

        except Exception as e:
            logger.error(f"Exception in send_brain_reports: {e}")
        finally:
            self.close_socket()

    def close_socket(self) -> None:
        """Closes the socket connection."""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

    def stop(self) -> None:
        self.running_status = False
        self.close_socket()


def main():
    # For sending brain reports
    client = FrHUBBrainReportClient(host=BRAIN_REPORT_HOST, port=BRAIN_REPORT_PORT)
    client_thread = threading.Thread(target=client.send_brain_report)
    client_thread.start()
    return client
