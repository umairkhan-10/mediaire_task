import socket
import threading

from fr_pacs.client import FrPACSBrainScanClient
from fr_pacs.server import FrPACSBrainReportServer


class TestFrPACSClient:
    def test_client_initialization(self):
        client = FrPACSBrainScanClient(host="127.0.0.1", port=12345)
        assert client.host == "127.0.0.1"
        assert client.port == 12345

    def test_send_brain_scan(self):
        client = FrPACSBrainScanClient(host="127.0.0.1", port=12345)
        assert client.client_socket is None

        def mock_sendall(data):
            assert data is not None

        client.client_socket = type('', (), {'sendall': mock_sendall, 'recv': lambda x: b'ack'})()
        client.send_brain_scan()


class TestFrPACSReportServer:
    def test_server_initialization(self):
        server = FrPACSBrainReportServer(host="127.0.0.1", port=12346)
        assert server.host == "127.0.0.1"
        assert server.port == 12346

    def test_handle_brain_report(self):
        server = FrPACSBrainReportServer(host="127.0.0.1", port=12346)
        server_thread = threading.Thread(target=server.run_brain_report_server)
        server_thread.start()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 12346))
        client_socket.sendall(b"Test brain report")
        response = client_socket.recv(1024).decode("utf-8")

        assert "FrPACS received the brain report successfully" in response

        client_socket.close()
        server.stop()
