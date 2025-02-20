import threading
import unittest
from unittest.mock import patch

from fr_brain.processor import FrBRAINScanProcessor


class TestFrBRAINScanProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = FrBRAINScanProcessor()
        self.processor.stop_after_one_iteration = True  # Set the flag to stop after one iteration

    @patch('fr_brain.processor.DBManager.insert')
    def test_process_brain_scans(self, mock_insert):
        """Test the process_brain_scans method"""

        # Run the processor in a separate thread
        processor_thread = threading.Thread(target=self.processor.process_brain_scans)
        processor_thread.start()

        # Allow some time for the thread to start and run one iteration
        processor_thread.join(timeout=2)

        # Ensure the insert method was called
        mock_insert.assert_called_once()

        # Stop the processor
        self.processor.stop()
        processor_thread.join(timeout=1)

        # Ensure the thread has stopped
        self.assertFalse(processor_thread.is_alive())

    # TODO: methods
    def fetch_and_process_scan(self, mock_stop):
        pass

    def test_stop(self):
        pass
    

if __name__ == '__main__':
    unittest.main()
