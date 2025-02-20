import socket
import threading
import time

import pytest

from common.config import BRAIN_SCAN_PORT, BRAIN_SCAN_HOST, BRAIN_REPORT_PORT, BRAIN_REPORT_HOST
from common.db_manager import DBManager
from fr_brain.processor import FrBRAINScanProcessor
from fr_hub.server import FrHUBBrainScanServer
from fr_pacs.server import FrPACSBrainReportServer


class TestIntegration:

    @pytest.fixture(scope="class")
    def start_servers(self):
        """Start all servers in separate threads."""
        # Start FrPACSBrainReportServer
        report_server = FrPACSBrainReportServer(host=BRAIN_REPORT_HOST, port=BRAIN_REPORT_PORT)
        report_server_thread = threading.Thread(target=report_server.run_brain_report_server)
        report_server_thread.start()

        # Start FrHUBBrainScanServer
        scan_server = FrHUBBrainScanServer(host=BRAIN_SCAN_HOST, port=BRAIN_SCAN_PORT)
        scan_server_thread = threading.Thread(target=scan_server.run_brain_scan_server)
        scan_server_thread.start()

        # Start FrBRAINScanProcessor
        processor = FrBRAINScanProcessor()
        processor_thread = threading.Thread(target=processor.process_brain_scans)
        processor_thread.start()

        yield

        # Stop servers and threads
        report_server.stop()
        scan_server.stop()
        processor.stop()
        report_server_thread.join()
        scan_server_thread.join()
        processor_thread.join()

    @pytest.fixture(scope="class")
    def setup_mocks(self, mocker):
        """Mock DBManager methods."""
        mocker.patch.object(DBManager, 'insert', return_value="123")
        mocker.patch.object(DBManager, 'fetch_one', return_value={"key": "value"})
        mocker.patch.object(DBManager, 'fetch_one_and_update', return_value={"key": "new_value"})
        mocker.patch.object(DBManager, 'fetch_all', return_value=[{"key": "value1"}, {"key": "value2"}])
        mocker.patch.object(DBManager, 'update', return_value=1)

    def test_integration(self, start_servers, setup_mocks):
        """Test the integration of all components."""
        # sending brain scan
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((BRAIN_SCAN_HOST, BRAIN_SCAN_PORT))
        client_socket.sendall(b"test brain scan")
        response = client_socket.recv(1024)
        client_socket.close()

        # Verifying the response from FrHUBBrainScanServer
        assert response == b"FRHub received the brain scan and successfully stored it"

        time.sleep(1)

        # Simulate sending a brain report from FrHUBBrainReportClient to FrPACSBrainReportServer
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((BRAIN_REPORT_HOST, BRAIN_REPORT_PORT))
        client_socket.sendall(b"test brain report")
        response = client_socket.recv(1024)
        client_socket.close()

        # Verify the response from FrPACSBrainReportServer
        assert response == b"FrPACS received the brain report successfully: test brain report"

        # Verify that the DBManager methods were called
        DBManager.insert.assert_called()
        DBManager.fetch_one.assert_called()
        DBManager.fetch_one_and_update.assert_called()
        DBManager.fetch_all.assert_called()
        DBManager.update.assert_called()


if __name__ == "__main__":
    pytest.main()
