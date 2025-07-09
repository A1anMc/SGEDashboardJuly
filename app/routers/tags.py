from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.tag import Tag, TagCategory
from app.models.user import User
from app.core.deps import get_current_user
from app.schemas.tag import TagCreate, TagUpdate, Tag as TagSchema, TagWithRelations

router = APIRouter()

@router.get("/", response_model=List[TagWithRelations])
async def get_tags(
    category: Optional[TagCategory] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all tags with optional filtering.
    """
    query = db.query(Tag)
    
    if category:
        query = query.filter(Tag.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Tag.name.ilike(search_term)) |
            (Tag.description.ilike(search_term)) |
            (Tag.synonyms.ilike(search_term))
        )
    
    # Count related entities
    tags = []
    for tag in query.offset(skip).limit(limit).all():
        grant_count = len(tag.grants)
        project_count = len(tag.projects)
        tag_dict = TagWithRelations.model_validate(tag).model_dump()
        tag_dict.update({
            "grant_count": grant_count,
            "project_count": project_count
        })
        tags.append(TagWithRelations(**tag_dict))
    
    return tags

@router.post("/", response_model=TagSchema, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new tag.
    Requires authentication.
    """
    # Check if tag with same name exists
    existing = db.query(Tag).filter(Tag.name == tag_in.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Tag with name '{tag_in.name}' already exists"
        )
    
    # Validate parent tag if provided
    if tag_in.parent_id:
        parent = db.query(Tag).filter(Tag.id == tag_in.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=404,
                detail=f"Parent tag with id {tag_in.parent_id} not found"
            )
        if parent.category != tag_in.category:
            raise HTTPException(
                status_code=400,
                detail="Parent tag must be in the same category"
            )
    
    # Create tag
    tag = Tag(
        **tag_in.model_dump(),
        created_by_id=current_user.id
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return tag

@router.get("/{tag_id}", response_model=TagWithRelations)
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific tag by ID.
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=404,
            detail=f"Tag with id {tag_id} not found"
        )
    
    grant_count = len(tag.grants)
    project_count = len(tag.projects)
    tag_dict = TagWithRelations.model_validate(tag).model_dump()
    tag_dict.update({
        "grant_count": grant_count,
        "project_count": project_count
    })
    
    return TagWithRelations(**tag_dict)

@router.put("/{tag_id}", response_model=TagSchema)
async def update_tag(
    tag_id: int,
    tag_in: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a tag.
    Requires authentication.
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=404,
            detail=f"Tag with id {tag_id} not found"
        )
    
    # Check name uniqueness if being updated
    if tag_in.name and tag_in.name != tag.name:
        existing = db.query(Tag).filter(Tag.name == tag_in.name).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Tag with name '{tag_in.name}' already exists"
            )
    
    # Validate parent tag if being updated
    if tag_in.parent_id and tag_in.parent_id != tag.parent_id:
        if tag_in.parent_id == tag_id:
            raise HTTPException(
                status_code=400,
                detail="Tag cannot be its own parent"
            )
        parent = db.query(Tag).filter(Tag.id == tag_in.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=404,
                detail=f"Parent tag with id {tag_in.parent_id} not found"
            )
        if parent.category != (tag_in.category or tag.category):
            raise HTTPException(
                status_code=400,
                detail="Parent tag must be in the same category"
            )
    
    # Update tag
    update_data = tag_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a tag.
    Requires authentication.
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=404,
            detail=f"Tag with id {tag_id} not found"
        )
    
    # Check if tag has children
    if tag.children:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete tag with child tags"
        )
    
    db.delete(tag)
    db.commit()
    
    return None

@router.get("/category/{category}", response_model=List[TagSchema])
async def get_tags_by_category(
    category: TagCategory,
    db: Session = Depends(get_db)
):
    """
    Get all tags in a specific category.
    """
    return db.query(Tag).filter(Tag.category == category).all()

@router.get("/search/", response_model=List[TagSchema])
async def search_tags(
    q: str = Query(..., min_length=2),
    category: Optional[TagCategory] = None,
    db: Session = Depends(get_db)
):
    """
    Search tags by name, description, or synonyms.
    """
    search_term = f"%{q}%"
    query = db.query(Tag).filter(
        (Tag.name.ilike(search_term)) |
        (Tag.description.ilike(search_term)) |
        (Tag.synonyms.ilike(search_term))
    )
    
    if category:
        query = query.filter(Tag.category == category)
    
    return query.all()

@router.get("/validate/{name}", response_model=bool)
async def validate_tag_name(
    name: str,
    exclude_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Check if a tag name is available.
    """
    query = db.query(Tag).filter(Tag.name == name)
    if exclude_id:
        query = query.filter(Tag.id != exclude_id)
    
    return not db.query(query.exists()).scalar() 