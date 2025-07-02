from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.grant import GrantModel
from app.schemas.grant import Grant, GrantCreate, GrantUpdate

router = APIRouter()

@router.get("/", response_model=List[Grant])
def get_grants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve grants with pagination.
    """
    grants = db.query(GrantModel).offset(skip).limit(limit).all()
    return [
        Grant(
            id=grant.id,
            title=grant.title,
            description=grant.description,
            source=grant.source,
            tags=grant.tags_list,
            created_at=grant.created_at,
            updated_at=grant.updated_at
        )
        for grant in grants
    ]

@router.post("/", response_model=Grant)
def create_grant(
    grant_in: GrantCreate,
    db: Session = Depends(get_db)
):
    """
    Create new grant.
    """
    grant = GrantModel(
        title=grant_in.title,
        description=grant_in.description,
        source=grant_in.source
    )
    grant.tags_list = grant_in.tags
    db.add(grant)
    db.commit()
    db.refresh(grant)
    return Grant(
        id=grant.id,
        title=grant.title,
        description=grant.description,
        source=grant.source,
        tags=grant.tags_list,
        created_at=grant.created_at,
        updated_at=grant.updated_at
    )

@router.get("/{grant_id}", response_model=Grant)
def get_grant(
    grant_id: int,
    db: Session = Depends(get_db)
):
    """
    Get grant by ID.
    """
    grant = db.query(GrantModel).filter(GrantModel.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return Grant(
        id=grant.id,
        title=grant.title,
        description=grant.description,
        source=grant.source,
        tags=grant.tags_list,
        created_at=grant.created_at,
        updated_at=grant.updated_at
    )

@router.put("/{grant_id}", response_model=Grant)
def update_grant(
    grant_id: int,
    grant_in: GrantUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a grant.
    """
    grant = db.query(GrantModel).filter(GrantModel.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    update_data = grant_in.model_dump(exclude_unset=True)
    if "tags" in update_data:
        grant.tags_list = update_data.pop("tags")
    for field, value in update_data.items():
        setattr(grant, field, value)
    
    db.add(grant)
    db.commit()
    db.refresh(grant)
    return Grant(
        id=grant.id,
        title=grant.title,
        description=grant.description,
        source=grant.source,
        tags=grant.tags_list,
        created_at=grant.created_at,
        updated_at=grant.updated_at
    )

@router.delete("/{grant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grant(
    grant_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a grant.
    """
    grant = db.query(GrantModel).filter(GrantModel.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    db.delete(grant)
    db.commit()
    return None