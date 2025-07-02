from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.program_logic import ProgramLogic as ProgramLogicModel
from app.schemas.program_logic import ProgramLogic, ProgramLogicCreate, ProgramLogicUpdate

router = APIRouter()

@router.get("/", response_model=List[ProgramLogic])
def get_program_logic_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve program logic entries with pagination.
    """
    entries = db.query(ProgramLogicModel).offset(skip).limit(limit).all()
    return entries

@router.post("/", response_model=ProgramLogic, status_code=status.HTTP_201_CREATED)
def create_program_logic(
    program_logic_in: ProgramLogicCreate,
    db: Session = Depends(get_db)
):
    """
    Create new program logic entry.
    """
    program_logic = ProgramLogicModel(**program_logic_in.model_dump())
    db.add(program_logic)
    db.commit()
    db.refresh(program_logic)
    return program_logic

@router.get("/{logic_id}", response_model=ProgramLogic)
def get_program_logic(
    logic_id: int,
    db: Session = Depends(get_db)
):
    """
    Get program logic entry by ID.
    """
    program_logic = db.query(ProgramLogicModel).filter(ProgramLogicModel.id == logic_id).first()
    if not program_logic:
        raise HTTPException(status_code=404, detail="Program Logic entry not found")
    return program_logic

@router.get("/project/{project_id}", response_model=List[ProgramLogic])
def get_program_logic_by_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all program logic entries for a specific project.
    """
    entries = db.query(ProgramLogicModel).filter(ProgramLogicModel.project_id == project_id).all()
    return entries

@router.put("/{logic_id}", response_model=ProgramLogic)
def update_program_logic(
    logic_id: int,
    program_logic_in: ProgramLogicUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a program logic entry.
    """
    program_logic = db.query(ProgramLogicModel).filter(ProgramLogicModel.id == logic_id).first()
    if not program_logic:
        raise HTTPException(status_code=404, detail="Program Logic entry not found")
    
    update_data = program_logic_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(program_logic, field, value)
    
    db.add(program_logic)
    db.commit()
    db.refresh(program_logic)
    return program_logic

@router.delete("/{logic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program_logic(
    logic_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a program logic entry.
    """
    program_logic = db.query(ProgramLogicModel).filter(ProgramLogicModel.id == logic_id).first()
    if not program_logic:
        raise HTTPException(status_code=404, detail="Program Logic entry not found")
    
    db.delete(program_logic)
    db.commit()
    return None