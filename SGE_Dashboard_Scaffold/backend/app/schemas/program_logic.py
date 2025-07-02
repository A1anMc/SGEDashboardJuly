from typing import Optional
from pydantic import BaseModel

class ProgramLogicBase(BaseModel):
    project_id: int
    input: str
    output: str
    outcome: str
    impact: str

class ProgramLogicCreate(ProgramLogicBase):
    pass

class ProgramLogicUpdate(ProgramLogicBase):
    project_id: Optional[int] = None
    input: Optional[str] = None
    output: Optional[str] = None
    outcome: Optional[str] = None
    impact: Optional[str] = None

class ProgramLogic(ProgramLogicBase):
    id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "project_id": 1,
                "input": "Funding, staff time, equipment",
                "output": "Produced 3 short films, 1 podcast series",
                "outcome": "Increased community engagement, skill development for interns",
                "impact": "Enhanced local arts scene, positive social change awareness"
            }
        } 