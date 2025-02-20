from strenum import StrEnum


class Queues(StrEnum):
    brain_scan = "brain_scan"
    brain_report = "brain_report"


class NeuroDataCollections(StrEnum):
    brain_scans = "brain_scans"
    brain_reports = "brain_reports"


class ReportStatus(StrEnum):
    to_do = "To Do"
    in_process = "In Process"
    done = "Done"
    error = "Error"


# should be in some env file or probably or some more secure Secrets Manager like AWS
MONGO_DB_URI = "mongodb://localhost:27017"
BRAIN_SCAN_HOST = "127.0.0.1"
BRAIN_SCAN_PORT = 12345

BRAIN_REPORT_HOST = "127.0.0.1"
BRAIN_REPORT_PORT = 12345
