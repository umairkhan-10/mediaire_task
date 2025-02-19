import base64
import json
import socket
import threading

from common.logger import logger
from common.utils import save_brain_scan, fetch_brain_report


class FrHUBClient:
    """Sends stored brain reports to FrPACS

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
        self.running = True

    def send_brain_report(self):
        """
        Sends brain reports to FrPACS.
        :return:
        """
        try:
            while self.running:
                try:
                    if not self.client_socket:
                        self.client_socket = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM
                        )
                        self.client_socket.connect((self.host, self.port))
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

        except Exception as e:
            logger.error(f"Exception in send_brain_reports: {e}")
        finally:
            self.close_socket()

    def close_socket(self):
        """Closes the socket connection."""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

    def stop(self):
        self.running = False
        self.close_socket()


class FrHUBServer:
    """Handles incoming brain scans from FrPACS

    Requirement:
        - Brain scan should be surviving reboots, hence it should be retried upon restarting
        - If FrHUB stops, FrPACS will continue generating brain scans, but they will not be received here, rather failed scans would only be logged (already logging in FRPACS)
        - It should conitnue processing scan after restarting
        - We are using simple network communication here while receiving brain scans since retry mechanisms and queuing mechanism is not needed.
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = True

    @staticmethod
    def handle_client(client_socket: socket.socket) -> None:
        """
        Handles incoming brain scans and stores them persistently (we could use any data store) and sends acknowledgenment to FrPACS.
        :param client_socket:
        :return:
        """
        try:
            while True:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    break

                logger.info(f"Received brain scan: {data}")
                brain_scan_data = json.loads(data)
                brain_scan_data[4] = base64.b64decode(brain_scan_data[4]).decode(
                    "utf-8"
                )

                # Saves the brain scan
                save_scan_response = save_brain_scan(tuple(brain_scan_data))
                if save_scan_response:
                    response = (
                        "FRHub received the brain scan and successfully stored it"
                    )
                    # Sending acknowledgement to FrPACS
                    client_socket.sendall(response.encode("utf-8"))
        except Exception as e:
            logger.error(f"Exception in handling brain scan: {e}")
        finally:
            if client_socket:
                client_socket.close()

    def run(self) -> None:
        """
        It will listen to incoming brain scans.
        :return:
        """
        try:
            if not self.server_socket:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(5)
                logger.info(
                    f"FrHUB is listening for brain scans on {self.host}:{self.port}"
                )

            while self.running:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"Connection is accepted from {addr}")
                client_handler = threading.Thread(
                    target=self.handle_client, args=(client_socket,)
                )
                client_handler.start()
        except Exception as e:
            logger.error(f"Exception while handling FrHUB server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()


def run_server():
    # Receiver for brain scan
    server = FrHUBServer(host="127.0.0.1", port=12345)
    server_thread = threading.Thread(target=server.run)
    server_thread.start()
    return server


def run_client():
    # For sending brain reports
    client = FrHUBClient(host="127.0.0.1", port=12346)
    client_thread = threading.Thread(target=client.send_brain_report)
    client_thread.start()
    return client


if __name__ == "__main__":
    server = run_server()
    client = run_client()

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        # terminate gracefully
        client.stop()
        server.stop()
        logger.info("FrHUB stopped successfully.")
