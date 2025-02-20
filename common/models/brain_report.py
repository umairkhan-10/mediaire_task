from datetime import datetime

from common.models.base import BaseDocument


class BrainReport(BaseDocument):
    report_datetime: datetime
    report_data: str
    sent: bool = False
