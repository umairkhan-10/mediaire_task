from typing import Dict, Any

from pydantic import BaseModel

from common.db_manager import DBManager

db_manager = DBManager()


class BaseDocument(BaseModel):
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
