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


MONGO_DB_URI = "mongodb://localhost:27017"
