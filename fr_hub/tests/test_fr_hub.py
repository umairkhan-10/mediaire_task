from datetime import datetime

from common.config import ReportStatus
from common.utils import save_brain_scan


def test_save_scan_data():
    invalid_scan_data = (None, 20, "| | o|", ReportStatus.to_do, "BRAIN", datetime.now())

    result = save_brain_scan(invalid_scan_data)

    assert result is False, "Processing invalid data should result an error"
