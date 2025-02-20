import socket
import threading

from common.config import BRAIN_REPORT_HOST, BRAIN_REPORT_PORT
from common.logger import logger


class FrPACSBrainReportServer:
    """Handles incoming brain report from FrHub

    Requirement:
        - Requirement is that it is OK if FrPACS stops at some point in time, brain reports sent from FrHUB will fail,
        - We don't need to persist that, we just need to log so simple network communicateion is fine here, no need for any persistent storage etc.

    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = None
        self.running_status = True

    @staticmethod
    def handle_brain_report(client_socket: socket.socket) -> None:
        """
        handles the brain reports coming from FrHUB

        :param client_socket:
        :return:
        """
        try:
            while True:
                brain_report_data = client_socket.recv(1024).decode("utf-8")
                if not brain_report_data:
                    break
                logger.info(f"Received brain report: {brain_report_data}")
                response = f"FrPACS received the brain report successfully: {brain_report_data}"
                # sending acknowledgement to FrHUB
                client_socket.sendall(response.encode("utf-8"))
        except Exception as e:
            logger.error(f"Exception while handling message: {e}")
        finally:
            # Close the connection to the client
            if client_socket:
                client_socket.close()

    def run_brain_report_server(self) -> None:
        """
        Runs the server to receive brain report coming from FrHUB
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
            while self.running_status:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"Connection is accepted from {addr}")
                client_handler = threading.Thread(
                    target=self.handle_brain_report, args=(client_socket,)
                )
                client_handler.start()
        except Exception as e:
            logger.error(f"Exception while handling FrPACS server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def stop(self) -> None:
        self.running_status = False
        if self.server_socket:
            self.server_socket.close()


def main():
    # Receiver for brain report
    server = FrPACSBrainReportServer(host=BRAIN_REPORT_HOST, port=BRAIN_REPORT_PORT)
    server_thread = threading.Thread(target=server.run_brain_report_server)
    server_thread.start()
    return server
