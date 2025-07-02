import pytest
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, computed_field, ConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from typing import List

# Assuming pytest is run from the project root ('sge_test_backend')
# this allows imports like 'from app.models...' to work correctly.
from app.db.base_class import Base
from app.models.grant import GrantModel


# --- Pydantic Schemas ---
# In a real app, these would be in `app/schemas/grant.py`

class GrantBase(BaseModel):
    title: str
    description: str | None = None
    source: str | None = None

class GrantCreate(GrantBase):
    tags_list: list[str] = []

class GrantUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    source: str | None = None
    tags_list: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)

class Grant(GrantBase):
    id: int
    tags_list: list[str] = []

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def tags(self) -> str | None:
        if self.tags_list:
            return ",".join(self.tags_list)
        return None


# --- Test-specific SQLAlchemy and FastAPI setup ---

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI app instance for testing
app = FastAPI()

# Dependency to get a DB session for a single request
def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints for testing ---
# In a real app, these would be in `app/api/endpoints/grants.py`

@app.get("/grants/", response_model=List[Grant])
def list_grants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List grants with pagination."""
    grants = db.query(GrantModel).offset(skip).limit(limit).all()
    return [
        Grant(
            id=grant.id,
            title=grant.title,
            description=grant.description,
            source=grant.source,
            tags_list=[tag.strip() for tag in grant.tags.split(",")] if grant.tags else []
        )
        for grant in grants
    ]

@app.post("/grants/", response_model=Grant)
def create_grant_endpoint(grant: GrantCreate, db: Session = Depends(get_db)):
    # Convert the list of tags into a comma-separated string for the DB
    grant_data = grant.model_dump(exclude={"tags_list"})
    grant_data["tags"] = ",".join(grant.tags_list) if grant.tags_list else None

    db_grant = GrantModel(**grant_data)
    db.add(db_grant)
    db.commit()
    db.refresh(db_grant)
    return Grant(
        id=db_grant.id,
        title=db_grant.title,
        description=db_grant.description,
        source=db_grant.source,
        tags_list=[tag.strip() for tag in db_grant.tags.split(",")] if db_grant.tags else []
    )

@app.get("/grants/{grant_id}", response_model=Grant)
def read_grant_endpoint(grant_id: int, db: Session = Depends(get_db)):
    db_grant = db.query(GrantModel).filter(GrantModel.id == grant_id).first()
    if db_grant is None:
        raise HTTPException(status_code=404, detail="Grant not found")
    return Grant(
        id=db_grant.id,
        title=db_grant.title,
        description=db_grant.description,
        source=db_grant.source,
        tags_list=[tag.strip() for tag in db_grant.tags.split(",")] if db_grant.tags else []
    )

@app.put("/grants/{grant_id}", response_model=Grant)
def update_grant_endpoint(
    grant_id: int,
    grant_update: GrantUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing grant."""
    db_grant = db.query(GrantModel).filter(GrantModel.id == grant_id).first()
    if db_grant is None:
        raise HTTPException(status_code=404, detail="Grant not found")

    update_data = grant_update.model_dump(exclude_unset=True)
    
    # Handle tags separately
    if "tags_list" in update_data:
        tags_list = update_data.pop("tags_list")
        db_grant.tags = ",".join(tags_list) if tags_list else None

    # Update other fields
    for field, value in update_data.items():
        setattr(db_grant, field, value)

    db.commit()
    db.refresh(db_grant)
    
    return Grant(
        id=db_grant.id,
        title=db_grant.title,
        description=db_grant.description,
        source=db_grant.source,
        tags_list=[tag.strip() for tag in db_grant.tags.split(",")] if db_grant.tags else []
    )

@app.delete("/grants/{grant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grant_endpoint(grant_id: int, db: Session = Depends(get_db)):
    """Delete a grant."""
    db_grant = db.query(GrantModel).filter(GrantModel.id == grant_id).first()
    if db_grant is None:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    db.delete(db_grant)
    db.commit()
    return None


# --- Pytest Fixtures ---

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture to set up and tear down the database for each test function.
    Creates the grants table before the test and drops it after.
    """
    Base.metadata.create_all(bind=engine)  # CREATE TABLES
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # DROP TABLES

@pytest.fixture(scope="function")
def client(db_session: Session):
    """Fixture to create a TestClient with an overridden DB dependency."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Clean up the override after the test
    app.dependency_overrides.clear()

@pytest.fixture
def sample_grants(db_session: Session):
    """Fixture to create sample grants for testing list and pagination."""
    grants = [
        GrantModel(
            title=f"Grant {i}",
            description=f"Description {i}",
            source=f"Source {i}",
            tags=f"tag{i},common"
        )
        for i in range(1, 4)  # Create 3 sample grants
    ]
    for grant in grants:
        db_session.add(grant)
    db_session.commit()
    for grant in grants:
        db_session.refresh(grant)
    return grants


# --- Pytest Test Functions ---

def test_create_grant(client: TestClient):
    """Test creating a new grant via the API with tags."""
    response = client.post(
        "/grants/",
        json={
            "title": "Test Grant with Tags",
            "description": "A grant for testing purposes",
            "tags_list": ["research", "education"]
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Test Grant with Tags"
    assert "id" in data
    # Check that the API correctly returns the list of tags
    assert data["tags_list"] == ["research", "education"]

def test_read_grant(client: TestClient, db_session: Session):
    """Test reading a grant and ensuring its tags string is converted to a list."""
    # Pre-populate the database directly with a comma-separated tags string
    new_grant = GrantModel(
        title="Pre-existing Grant",
        source="Fixture",
        tags="science,health"
    )
    db_session.add(new_grant)
    db_session.commit()
    db_session.refresh(new_grant)

    grant_id = new_grant.id

    # Make the API call to the GET endpoint
    response = client.get(f"/grants/{grant_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Pre-existing Grant"
    assert data["id"] == grant_id
    # Check that the API correctly converted the DB string to a list
    assert data["tags_list"] == ["science", "health"]

def test_read_nonexistent_grant(client: TestClient):
    """Test that reading a grant that does not exist returns a 404 error."""
    response = client.get("/grants/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Grant not found"}

def test_list_grants(client: TestClient, sample_grants):
    """Test listing all grants with default pagination."""
    response = client.get("/grants/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # We created 3 sample grants
    # Check the first grant
    assert data[0]["title"] == "Grant 1"
    assert "common" in data[0]["tags_list"]
    assert "tag1" in data[0]["tags_list"]

def test_list_grants_pagination(client: TestClient, sample_grants):
    """Test grant listing with pagination."""
    # Get first two grants
    response = client.get("/grants/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Grant 1"
    assert data[1]["title"] == "Grant 2"

    # Get the last grant
    response = client.get("/grants/?skip=2&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Grant 3"

def test_update_grant(client: TestClient, db_session: Session):
    """Test updating an existing grant."""
    # Create a grant first
    grant = GrantModel(
        title="Original Title",
        description="Original Description",
        source="Original Source",
        tags="old,tags"
    )
    db_session.add(grant)
    db_session.commit()
    db_session.refresh(grant)

    # Update the grant
    update_data = {
        "title": "Updated Title",
        "tags_list": ["new", "updated", "tags"]
    }
    response = client.put(f"/grants/{grant.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check that specified fields were updated
    assert data["title"] == "Updated Title"
    assert data["tags_list"] == ["new", "updated", "tags"]
    # Check that unspecified fields remain unchanged
    assert data["description"] == "Original Description"
    assert data["source"] == "Original Source"

def test_update_nonexistent_grant(client: TestClient):
    """Test updating a grant that doesn't exist."""
    response = client.put(
        "/grants/999",
        json={"title": "Updated Title"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Grant not found"}

def test_delete_grant(client: TestClient, db_session: Session):
    """Test deleting a grant."""
    # Create a grant first
    grant = GrantModel(
        title="To Be Deleted",
        description="This grant will be deleted",
        tags="delete,me"
    )
    db_session.add(grant)
    db_session.commit()
    db_session.refresh(grant)
    grant_id = grant.id

    # Delete the grant
    response = client.delete(f"/grants/{grant_id}")
    assert response.status_code == 204

    # Verify the grant is deleted
    response = client.get(f"/grants/{grant_id}")
    assert response.status_code == 404

def test_delete_nonexistent_grant(client: TestClient):
    """Test deleting a grant that doesn't exist."""
    response = client.delete("/grants/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Grant not found"} 