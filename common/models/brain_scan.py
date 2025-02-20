from datetime import datetime

from common.config import ReportStatus
from common.models.base import BaseDocument


class BrainScan(BaseDocument):
    scan_datetime: datetime
    scan_type: str
    scan_data: str
    report_generated: bool = ReportStatus.to_do
