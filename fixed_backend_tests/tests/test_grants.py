import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base_class import Base
from app.models.grant import GrantModel
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# FastAPI app
app = FastAPI()

# SQLite in-memory engine
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override
def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/grants/")
def create_grant(grant: dict, db: Session = Depends(get_db)):
    grant_obj = GrantModel(**grant)
    db.add(grant_obj)
    db.commit()
    db.refresh(grant_obj)
    return grant_obj

@app.get("/api/grants/{grant_id}")
def get_grant(grant_id: int, db: Session = Depends(get_db)):
    grant = db.query(GrantModel).filter(GrantModel.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_grant(client):
    response = client.post("/api/grants/", json={
        "title": "Test Grant",
        "description": "Testing",
        "source": "Test Source",
        "tags": "test"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Grant"

    response = client.get(f"/api/grants/{data['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == data["id"]