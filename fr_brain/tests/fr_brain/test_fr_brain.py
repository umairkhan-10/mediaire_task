import time

from common.const import ReportStatus, NeuroDataCollections
from fr_brain.main import run_brain_processor


def test_fr_brain_processor_functionality(db_manager):
    # Insert a brain scan into the database
    scan_data = {
        "patient_id": 1,
        "scan_id": 20,
        "scan_data": "| |     |o|",
        "report_generated": ReportStatus.to_do,
        "scan_type": "BRAIN",
        "scan_datetime": time.time(),
    }
    db_manager.insert(NeuroDataCollections.brain_scans, scan_data)

    # Start the brain processor
    brain_instance = run_brain_processor()

    # Allow some time for the brain processor to process the scan
    time.sleep(10)

    # Verify that the brain scan was processed
    processed_scan = db_manager.fetch_one(
        NeuroDataCollections.brain_scans, {"scan_id": 20}
    )
    assert processed_scan is not None
    assert processed_scan["report_generated"] == ReportStatus.done

    # Stop the brain processor
    brain_instance.stop()
