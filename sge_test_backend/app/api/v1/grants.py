from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.grant import Grant
from app.schemas.grant import (
    GrantCreate,
    GrantUpdate,
    GrantResponse,
    GrantList
)

router = APIRouter()

@router.get("", response_model=GrantList)
def list_grants(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = None,
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0, le=100)
) -> GrantList:
    """
    Retrieve grants with filtering and pagination.
    """
    skip = (page - 1) * size
    query = db.query(Grant)

    if status:
        query = query.filter(Grant.status == status)
    if tags:
        for tag in tags:
            query = query.filter(Grant.tags.contains([tag]))
    if search:
        query = query.filter(
            Grant.title.ilike(f"%{search}%") |
            Grant.description.ilike(f"%{search}%")
        )

    total = query.count()
    grants = query.offset(skip).limit(size).all()

    return GrantList(
        items=grants,
        total=total,
        page=page,
        size=size
    )

@router.post("", response_model=GrantResponse, status_code=201)
def create_grant(
    grant_in: GrantCreate,
    db: Session = Depends(get_db)
) -> Grant:
    """
    Create a new grant.
    """
    grant = Grant(**grant_in.model_dump())
    db.add(grant)
    db.commit()
    db.refresh(grant)
    return grant

@router.get("/{grant_id}", response_model=GrantResponse)
def get_grant(
    grant_id: int,
    db: Session = Depends(get_db)
) -> Grant:
    """
    Get a specific grant by ID.
    """
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant

@router.put("/{grant_id}", response_model=GrantResponse)
def update_grant(
    grant_id: int,
    grant_in: GrantUpdate,
    db: Session = Depends(get_db)
) -> Grant:
    """
    Update a grant.
    """
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")

    for field, value in grant_in.model_dump(exclude_unset=True).items():
        setattr(grant, field, value)

    db.commit()
    db.refresh(grant)
    return grant

@router.delete("/{grant_id}", status_code=204)
def delete_grant(
    grant_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a grant.
    """
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")

    db.delete(grant)
    db.commit()

@router.get("/tags", response_model=List[str])
def get_tags(
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Get all unique tags from grants.
    """
    grants = db.query(Grant).all()
    tags = set()
    for grant in grants:
        tags.update(grant.tags)
    return sorted(list(tags)) 