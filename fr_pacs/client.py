import base64
import json
import random as rn
import socket
import threading
from datetime import datetime

from common.config import BRAIN_SCAN_PORT, BRAIN_SCAN_HOST
from common.logger import logger
from common.utils import generate_brain_scan


class FrPACSBrainScanClient:
    """
    Client for sending bran scan for FrHub

    Requirement:
        - Here the requirement was if FrHUB stops, FrPACS should just log those failed cases instead of persisting the data
        - So, first I am connecting to server (success or failure doesn't matter),
            creating brain scans and then trying to send the scan. If connections is successful, it'll be sent else it's going to log the failed sent scan

    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.client_socket = None
        self.running_status = True

    def send_brain_scan(self) -> None:
        """
        Sends the brain scan to FrHUB
        :return:
        """
        try:

            while self.running_status:
                # generating the scans
                patient_id = rn.randint(1, 1000)
                scan_id = rn.randint(1, 10000)
                scan_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                scan_data = generate_brain_scan()
                # encoding the data here
                encoded_scan = base64.b64encode(scan_data.encode("utf-8")).decode(
                    "utf-8"
                )
                data_to_send = json.dumps(
                    (patient_id, scan_id, scan_datetime, "BRAIN", encoded_scan)
                )

                # connecting the client and sending rbain scans
                # here successful connection doesn't matter as per given requriements
                try:
                    if not self.client_socket:
                        self.client_socket = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM
                        )
                        self.client_socket.connect((self.host, self.port))

                    # sending the scan
                    logger.info(f"Sending brain scan to FrHUB: {data_to_send}")
                    self.client_socket.sendall(data_to_send.encode("utf-8"))
                    # receiving an acknowledgement from FrHub
                    response = self.client_socket.recv(1024).decode("utf-8")
                    logger.info(f"Received an acknowledgment in FrPACS from FrHUB: {response}")
                except Exception as e:
                    logger.error(f"Exception while sending brain scans: {e}")
                    # as per requirement, we only need to log the failed cases if scan couldn't get sent, no need to persist it
                    logger.error(f"This scan isn't being sent: {scan_data}")

                    # in case if FrHub suddenly stops so it'll come to exception when sending the data,
                    # To survive reboots - we have to make sure it gets closed and then empty so that in next loop FrPACS can try to re-connect again (to check if FrHUB is restarted)
                    self.close_socket()

        except Exception as e:
            logger.error(f"Exception in send_brain_scan: {e}")
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
    # For sending brain scan
    client = FrPACSBrainScanClient(host=BRAIN_SCAN_HOST, port=BRAIN_SCAN_PORT)
    client_thread = threading.Thread(target=client.send_brain_scan)
    client_thread.start()
    return client
