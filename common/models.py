from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel

from common.const import ReportStatus
from common.db_manager import DBManager

db_manager = DBManager()


class BaseDocument(BaseModel):
    # id: Optional[ObjectId] = Field(None, alias="_id")
    patient_id: int
    scan_id: int

    class Config:
        arbitrary_types_allowed = True

    def to_bson(self) -> Dict[str, Any]:
        """Convert model to BSON (MongoDB document format)."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data:
            data.pop("_id")
        return data

    def insert(self, collection_name: str) -> Optional[str]:
        """Insert document into MongoDB."""
        return db_manager.insert(collection_name, self.to_bson())

    def update(self, collection_name: str, query: Dict[str, Any]) -> Optional[str]:
        """Update document in MongoDB."""
        return db_manager.update(collection_name, query, self.to_bson())


class BrainScan(BaseDocument):
    scan_datetime: datetime
    scan_type: str
    scan_data: str
    report_generated: bool = ReportStatus.to_do


class BrainReport(BaseDocument):
    report_datetime: datetime
    report_data: str
    sent: bool = False
