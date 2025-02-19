from common.const import ReportStatus
from common.utils import save_brain_scan


def test_save_scan_data():
    invalid_scan_data = {
        "patient_id": None,  # Missing patient ID
        "scan_id": 20,
        "scan_data": "| | o|",  # No lesion
        "report_generated": ReportStatus.to_do,
        "scan_type": "BRAIN",
        "scan_datetime": 1234567890,
    }

    result = save_brain_scan(invalid_scan_data)

    assert result is False, "Processing invalid data should result an error"
