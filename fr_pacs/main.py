import base64
import json
import random as rn
import socket
import threading
from datetime import datetime

from common.logger import logger
from common.utils import generate_brain_scan


class FrPACSClient:
    """
    Client for sending bran scan for FrHub

    Requirement:
        - Here the requirement was if FrHUB stops, FrPACS should just log those failed cases instead of persisting the data
       -  We could also integrate queue instead of sending brain scan directly but as per requirement, there is no use for it
        - So, first I am connecting to server (success or failure doesn't matter),
            creating brain scans and then trying to send the scan. If connections is successful, it'll be sent else it's going to log the failed sent scan

    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = True

    def send_brain_scan(self) -> None:
        """
        Sends the brain scan
        :return:
        """
        try:

            while self.running:
                # generating the scans
                patient_id = rn.randint(1, 1000)
                scan_id = rn.randint(1, 10000)
                scan_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                scan_data = generate_brain_scan()
                # encoding the data here
                # we can use much better encryption/decryption if we want to.
                encoded_scan = base64.b64encode(scan_data.encode("utf-8")).decode(
                    "utf-8"
                )
                data_to_send = json.dumps(
                    (patient_id, scan_id, scan_datetime, "BRAIN", encoded_scan)
                )

                # connecting the client and sending rbain scans
                # here successful connection doesn't matter as per given requriements
                # so no retry mechanism
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
                    logger.info(f"Received an acknowledgment from FrHUB: {response}")
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
        self.running = False
        self.close_socket()


class FrPACSServer:
    """Handles incoming brain report from FrHub

    Requirement:
        - Requirement is that it is OK if FrPACS stops at some point in time, brain reports sent from FrHUB will fail,
        - We don't need to persist that, we just need to log so simple network communicateion is fine here, no need for any fancy queue etc.

    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = True

    @staticmethod
    def handle_client(client_socket: socket.socket) -> None:
        """
        handles the brain reports that are coming to this port

        :param client_socket:
        :return:
        """
        try:
            while True:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    break
                logger.info(f"Received brain report: {data}")
                response = "FrPACS received the brain report successfully: " + data
                # sending acknowledgement to FrHUB
                client_socket.sendall(response.encode("utf-8"))
        except Exception as e:
            logger.error(f"Exception while handling message: {e}")
        finally:
            # Close the connection to the client
            # we could use via "with" as well
            if client_socket:
                client_socket.close()

    def run(self) -> None:
        """
        Runs the socket server
        :return:
        """
        try:
            if not self.server_socket:
                # socket object
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # binding to the host and port
                self.server_socket.bind((self.host, self.port))
                # enabling server to accept connections
                self.server_socket.listen(5)
                logger.info(
                    f"FrPACS is listening for brain reports on {self.host}:{self.port}"
                )

            # server is listening here
            while True:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"Connection is accepted from {addr}")
                client_handler = threading.Thread(
                    target=self.handle_client, args=(client_socket,)
                )
                client_handler.start()
        except Exception as e:
            logger.error(f"Exception while handling FrPACS server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def stop(self) -> None:
        self.running = False
        if self.server_socket:
            self.server_socket.close()


def run_client():
    # For sending brain scan
    client = FrPACSClient(host="127.0.0.1", port=12345)
    client_thread = threading.Thread(target=client.send_brain_scan)
    client_thread.start()
    return client


def run_server():
    # Receiver for brain report
    server = FrPACSServer(host="127.0.0.1", port=12346)
    server_thread = threading.Thread(target=server.run)
    server_thread.start()
    return server


if __name__ == "__main__":
    client = run_client()
    server = run_server()

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        # terminate gracefully
        client.stop()
        server.stop()
        logger.info("FrPACS stopped successfully.")
