import socket
import threading
import unittest
from unittest.mock import patch, MagicMock

from fr_pacs.client import FrPACSBrainScanClient


class TestFrPACSBrainScanClient(unittest.TestCase):

    def setUp(self):
        self.host = "127.0.0.1"
        self.port = 12345
        self.client = FrPACSBrainScanClient(host=self.host, port=self.port)
        self.client.running_status = True

    @patch('socket.socket')
    def test_send_brain_scan_success(self, mock_socket):
        """Test successful brain scan case"""

        # Setup mock socket
        mock_client_socket = MagicMock()
        mock_socket.return_value = mock_client_socket
        mock_client_socket.sendall.return_value = None
        mock_client_socket.close.return_value = None

        # Running `send_brain_scan` in a separate thread
        scan_thread = threading.Thread(target=self.client.send_brain_scan)
        scan_thread.start()

        # Stop client after short delay
        self.client.stop()
        scan_thread.join(timeout=1)  # Ensure the thread stops within 1 second

        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_client_socket.connect.assert_called_once_with(('127.0.0.1', 12345))
        mock_client_socket.sendall.assert_called()

        # socket is closed
        mock_client_socket.close.assert_called_once()

        # Thread has stopped
        self.assertFalse(scan_thread.is_alive())

    # TODO: Should write more test cases, some definitions are given below
    def test_send_brain_scan_failure(self):
        pass

    def test_send_brain_scan_socket_creation_failure(self):
        pass

    def test_send_brain_scan_receives_acknowledgment(self):
        pass

    def test_send_brain_scan_close_socket(self):
        pass


if __name__ == '__main__':
    unittest.main()
