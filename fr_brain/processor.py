import multiprocessing
import time

from common.config import NeuroDataCollections, ReportStatus
from common.db_manager import DBManager
from common.logger import logger
from common.utils import analyze_scan, save_brain_report


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

    def fetch_and_process_scan(self, scan_id):
        """Processes single brain scan and generate report"""
        db_manager = DBManager()
        try:
            # we're udpating a scan to 'In Process' so that other processes knows that this scan in being processed not pick this scan
            scan = db_manager.fetch_one_and_update(
                NeuroDataCollections.brain_scans,
                {"_id": scan_id},
                {"report_generated": ReportStatus.in_process}
            )
            if scan:
                logger.info(f"Processing scan: {scan_id}")
                # analyzing the scan data to find lesions
                scan["report_data"] = analyze_scan(scan["scan_data"])
                # saving the report to the DB
                save_report_response = save_brain_report(scan)
                if save_report_response:
                    logger.info(
                        f"Generated and saved report, for scan ID {scan_id}"
                    )
                    # after successful process, have to update the status of this scan as 'Done' in DB
                    db_manager.update(
                        NeuroDataCollections.brain_scans,
                        {"_id": scan_id},
                        {"report_generated": ReportStatus.done}
                    )
                    logger.info(f"Finished processing scan: {scan_id}")
        except Exception as e:
            # changing report status to 'Error' in case an exception occurs while processing this scan
            logger.error(f"Error processing this scan {scan_id}: {e}")
            db_manager.update(
                NeuroDataCollections.brain_scans,
                {"_id": scan_id},
                {"report_generated": ReportStatus.error}
            )

    def process_brain_scans(self) -> None:
        """Processes all available brain scans"""
        try:
            while self.running:
                # to avoid issues of pickling
                db_manager = DBManager()
                # fetching only those scans, whose reports are not yet generated
                all_scans = db_manager.fetch_all(
                    NeuroDataCollections.brain_scans,
                    {"report_generated": ReportStatus.to_do}
                )
                if all_scans:
                    # processing scans in multiprocessing environment
                    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                        pool.map(self.fetch_and_process_scan, [scan["_id"] for scan in all_scans])
                else:
                    logger.info("No pending scans to process. Waiting for scan...")
                    # sleep for 5 seconds before checking again as there is no scan
                    time.sleep(5)
        except Exception as e:
            logger.error(f"Exception in processing brain scans: {e}")

    def stop(self) -> None:
        """Stops the processing of brain scans."""
        self.running = False
