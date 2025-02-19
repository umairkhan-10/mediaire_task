import random as rn
from datetime import datetime

from common.const import NeuroDataCollections
from common.db_manager import DBManager
from common.logger import logger
from common.models import BrainScan, BrainReport

db_manager = DBManager()


def generate_brain_scan(rows=10, cols=10, lesion_prob=0.2) -> str:
    """
    Generates random brain scan of10*10 grid where each cell having probability of 20% lesion i.e. 'o'
    :param rows:
    :param cols:
    :param lesion_prob:
    :return:
    """
    scan = ""
    for _ in range(rows):
        row = "".join(
            rn.choice(["| |", "|o|"]) if rn.random() < lesion_prob else " "
            for _ in range(cols)
        )
        scan += row + "\n"
    return scan


def save_brain_scan(scan_data: tuple) -> bool:
    """Saves brain scan in DB"""
    try:
        brain_scan = BrainScan(
            patient_id=scan_data[0],
            scan_id=scan_data[1],
            scan_datetime=scan_data[2],
            scan_type=scan_data[3],
            scan_data=scan_data[4],
        )
        db_manager.insert(NeuroDataCollections.brain_scans, brain_scan.to_bson())
        return True
    except Exception as e:
        logger.error(f"Failed to save brain scan: {e}")
        return False


def analyze_scan(scan_data: str) -> str:
    """Analyzes the brain scan to find lesions."""
    lesion_count = scan_data.count("o")
    return f"The analysed scan showed {lesion_count} brain lesions."


def save_brain_report(report_data: dict) -> bool:
    """saves brain report into DB"""
    try:
        # we need to keep metadata as well as "sent" (default False) which will tell FrHUB taht this report is not being sent to FrPACS
        brain_report = BrainReport(
            patient_id=report_data["patient_id"],
            scan_id=report_data["scan_id"],
            report_datetime=datetime.now(),
            report_data=report_data["report_data"],
            sent=False,
        )
        db_manager.insert(NeuroDataCollections.brain_reports, brain_report.to_bson())
        return True
    except Exception as e:
        logger.error(f"Failed to save brain report: {e}")
        return False


def fetch_brain_report() -> dict | None:
    """Fetch brain report as well as update its staus as Sent to avoid duplicate sending"""
    report = db_manager.fetch_one_and_update(
        NeuroDataCollections.brain_reports,
        {"sent": False},
        {"$set": {"sent": True}},
    )
    if report:
        report_data = {
            "patient_id": report["patient_id"],
            "scan_id": report["scan_id"],
            "report_datetime": report["report_datetime"],
            "report_data": report["report_data"],
        }
        return report_data
    return None
