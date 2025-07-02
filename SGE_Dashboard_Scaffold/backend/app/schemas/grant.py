from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class GrantBase(BaseModel):
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    deadline: Optional[date] = None
    tags: List[str] = []

class GrantCreate(GrantBase):
    pass

class GrantUpdate(GrantBase):
    title: Optional[str] = None

class Grant(GrantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Arts & Culture Development Grant",
                "description": "Funding for innovative artistic projects.",
                "source": "State Arts Council",
                "deadline": "2024-12-31",
                "tags": ["arts", "culture", "development"],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    ) 