from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.grant import GrantModel

def test_create_grant(client: TestClient):
    grant_data = {
        "title": "Test Grant",
        "description": "Test Description",
        "source": "Test Source",
        "tags": ["test"]
    }
    response = client.post("/api/grants/", json=grant_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Grant"
    assert data["description"] == "Test Description"
    assert data["source"] == "Test Source"
    assert data["tags"] == ["test"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_read_grant(client: TestClient, db: Session):
    # Create a grant first
    grant = GrantModel(
        title="Test Grant",
        description="Test Description",
        source="Test Source"
    )
    grant.tags_list = ["test"]
    db.add(grant)
    db.commit()
    db.refresh(grant)

    response = client.get(f"/api/grants/{grant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Grant"
    assert data["description"] == "Test Description"
    assert data["source"] == "Test Source"
    assert data["tags"] == ["test"]
    assert data["id"] == grant.id

def test_read_nonexistent_grant(client: TestClient):
    response = client.get("/api/grants/999")
    assert response.status_code == 404

def test_update_grant(client: TestClient, db: Session):
    # Create a grant first
    grant = GrantModel(
        title="Original Title",
        description="Original Description",
        source="Original Source"
    )
    grant.tags_list = ["original"]
    db.add(grant)
    db.commit()
    db.refresh(grant)

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "source": "Updated Source",
        "tags": ["updated"]
    }
    response = client.put(f"/api/grants/{grant.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["source"] == update_data["source"]
    assert data["tags"] == update_data["tags"]

def test_delete_grant(client: TestClient, db: Session):
    # Create a grant first
    grant = GrantModel(
        title="To Be Deleted",
        source="Test Source"
    )
    grant.tags_list = []
    db.add(grant)
    db.commit()
    db.refresh(grant)

    response = client.delete(f"/api/grants/{grant.id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/grants/{grant.id}")
    assert get_response.status_code == 404 