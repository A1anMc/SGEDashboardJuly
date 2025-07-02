from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class MetricBase(BaseModel):
    project_id: int
    name: str
    value: float
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None

class MetricCreate(MetricBase):
    pass

class MetricUpdate(MetricBase):
    project_id: Optional[int] = None
    name: Optional[str] = None
    value: Optional[float] = None

class Metric(MetricBase):
    id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "project_id": 1,
                "name": "Audience Reach",
                "value": 15000.0,
                "unit": "people",
                "timestamp": "2025-06-30T10:00:00Z"
            }
        } 