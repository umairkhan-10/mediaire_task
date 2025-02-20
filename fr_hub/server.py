import base64
import json
import socket
import threading

from common.config import BRAIN_SCAN_PORT, BRAIN_SCAN_HOST
from common.logger import logger
from common.utils import save_brain_scan


class FrHUBBrainScanServer:
    """Handles incoming brain scans from FrPACS

    Requirement:
        - Brain scan should be surviving reboots, hence it should be retried upon restarting
        - If FrHUB stops, FrPACS will continue generating brain scans, but they will not be received here, rather failed scans would only be logged (already logging in FRPACS)
        - It should conitnue processing scan after restarting
        - We are using simple network communication here while receiving brain scans
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = None
        self.running_status = True

    @staticmethod
    def handle_brain_scan(client_socket: socket.socket) -> None:
        """
        Handles incoming brain scans and stores them persistently (we could use any data store) and sends acknowledgenment to FrPACS.
        :param client_socket:
        :return:
        """
        try:
            while True:
                brain_scan_data = client_socket.recv(1024).decode("utf-8")
                if not brain_scan_data:
                    break

                logger.info(f"Received brain scan: {brain_scan_data}")
                brain_scan_data = json.loads(brain_scan_data)
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
                    logger.info(f"Brain Scan received and saved via FrHUB: {save_scan_response}")
        except Exception as e:
            logger.error(f"Exception in handling brain scan: {e}")
        finally:
            if client_socket:
                client_socket.close()

    def run_brain_scan_server(self) -> None:
        """
        It will listen to incoming brain scans.
        :return:
        """
        try:
            if not self.server_socket:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # binding to the host and port
                self.server_socket.bind((self.host, self.port))
                # enabling server to accept connections
                self.server_socket.listen(5)
                logger.info(
                    f"FrHUB is listening for brain scans on {self.host}:{self.port}"
                )
            # server is listening here
            while self.running_status:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"Connection is accepted from {addr}")
                client_handler = threading.Thread(
                    target=self.handle_brain_scan, args=(client_socket,)
                )
                client_handler.start()
        except Exception as e:
            logger.error(f"Exception while handling FrHUB server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def stop(self) -> None:
        self.running_status = False
        if self.server_socket:
            self.server_socket.close()


def main():
    # Receiver for brain scan
    server = FrHUBBrainScanServer(host=BRAIN_SCAN_HOST, port=BRAIN_SCAN_PORT)
    server_thread = threading.Thread(target=server.run_brain_scan_server())
    server_thread.start()
    return server
