from datetime import datetime

import pytest

from common.const import NeuroDataCollections
from common.db_manager import DBManager


@pytest.fixture(scope="function")
def db_manager(mongodb_container):
    test_uri = f"mongodb://{mongodb_container.client.address[0]}:{mongodb_container.client.address[1]}"
    return DBManager(uri=test_uri)


def test_insert_and_fetch_one(db_manager):
    data = {
        "patient_id": 1,
        "scan_id": 20,
        "scan_data": "| |     |o|",
        "report_generated": "To Do",
        "scan_type": "BRAIN",
        "scan_datetime": datetime.now(),
    }
    inserted_id = db_manager.insert(NeuroDataCollections.brain_scans, data)
    assert inserted_id is not None

    fetched_data = db_manager.fetch_one(
        NeuroDataCollections.brain_scans, {"_id": inserted_id}
    )
    assert fetched_data is not None
    assert fetched_data["scan_id"] == 20
