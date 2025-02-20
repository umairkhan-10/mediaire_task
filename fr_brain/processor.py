import threading
import time

from common.config import NeuroDataCollections, ReportStatus
from common.db_manager import DBManager
from common.logger import logger
from common.utils import analyze_scan, save_brain_report

db_manager = DBManager()


class FrBRAINScanProcessor:
    """Processes brain scans from DB and generates report
    Requirement:
        - After generating report, it should be available for FRHUB, so need to store it in some persistant storage (DB)
        - Fr-BRAIN interacts with the same persistent storage that Fr-HUB interacts with (hence same DB)
        - it should be possible to stop Fr-BRAIN at any point, start it again at any other point in time, and it will consume the pending brain reports that were not yet processed
            So, we're keeping flag in brain_scan collection so we'll fetch only those brain scans i.e. "report_generated" as "To Do"
             ('To Do' means report yet to be processed), make it 'In Progress' when processing is beign done and make it 'Done' when it's done
        - Above will also cover the requirement, even if multiple instances of BrainProcessor runs, we'll only generate report for each scan only Once via above key
    """

    def __init__(self) -> None:
        self.running = True

    def process_brain_scans(self) -> None:
        """Processes the brain scans nd generate report."""
        try:
            while self.running:
                # fetching only those scans, whose reports are not yet generated and updating the report_generated of scan as "In Process"
                # so that no other running instance of FrBRAINProcessor can take the same scan to process
                scan_data = db_manager.fetch_one_and_update(
                    NeuroDataCollections.brain_scans,
                    {"report_generated": ReportStatus.to_do},
                    {"$set": {"report_generated": ReportStatus.in_process}},
                )
                # Currently, there is no retry mechansim right now if it fails after this step then, status of this report will always be In Process
                if scan_data:
                    try:
                        scan_data["report_data"] = analyze_scan(scan_data["scan_data"])
                        save_report_response = save_brain_report(scan_data)
                        if save_report_response:
                            logger.info(
                                f"Generated report, for scan ID {scan_data["scan_id"]}"
                            )
                            # Update the brain scan to mark it as processed
                            db_manager.update(
                                NeuroDataCollections.brain_scans,
                                {"scan_id": scan_data["scan_id"]},
                                {"report_generated": ReportStatus.done},
                            )
                    except Exception as e:
                        logger.error(f"Error creating brain scan after it's in In Process: {e}")
                        db_manager.update(
                            NeuroDataCollections.brain_scans,
                            {"_id": scan_data["_id"]},  # Update this specific scan only
                            {"$set": {"report_generated": ReportStatus.error}},
                        )
                else:
                    logger.info("No pending scans to process. Waiting for scan...")
                    # sleep for 5 seconds before checking again as there is no scan
                    time.sleep(5)
            # means the report scan status is changed to 'In Process' but after that an exception ocurred while geenrating report, we'd have to change it to 'Error'




        except Exception as e:
            logger.error(f"Exception in processing brain scans: {e}")

    def stop(self) -> None:
        """Stops the processing of brain scans."""
        self.running = False


def main():
    """starting the brain processor in separate thread"""
    brain_instance = FrBRAINScanProcessor()
    processing_thread = threading.Thread(target=brain_instance.process_brain_scans)
    processing_thread.start()
    return brain_instance
