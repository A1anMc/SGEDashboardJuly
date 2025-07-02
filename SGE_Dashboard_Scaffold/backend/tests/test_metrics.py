from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.metric import Metric as MetricModel
from app.schemas.metric import MetricCreate

def test_create_metric(client: TestClient, db: Session):
    metric_data = {
        "project_id": 1,
        "name": "Test Metric",
        "value": 100.0,
        "unit": "count",
        "timestamp": datetime.utcnow().isoformat()
    }
    response = client.post("/api/metrics/", json=metric_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == metric_data["name"]
    assert data["value"] == metric_data["value"]
    assert data["id"]

def test_read_metric(client: TestClient, db: Session):
    # Create a metric first
    metric = MetricModel(
        project_id=1,
        name="Test Metric",
        value=100.0,
        unit="count",
        timestamp=datetime.utcnow()
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)

    response = client.get(f"/api/metrics/{metric.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Metric"
    assert data["id"] == metric.id

def test_read_metrics_by_project(client: TestClient, db: Session):
    # Create multiple metrics for the same project
    project_id = 1
    for i in range(3):
        metric = MetricModel(
            project_id=project_id,
            name=f"Metric {i}",
            value=float(i * 100),
            unit="count"
        )
        db.add(metric)
    db.commit()

    response = client.get(f"/api/metrics/project/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(m["project_id"] == project_id for m in data)

def test_read_nonexistent_metric(client: TestClient):
    response = client.get("/api/metrics/999")
    assert response.status_code == 404

def test_update_metric(client: TestClient, db: Session):
    # Create a metric first
    metric = MetricModel(
        project_id=1,
        name="Original Name",
        value=100.0
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)

    update_data = {
        "name": "Updated Name",
        "value": 200.0
    }
    response = client.put(f"/api/metrics/{metric.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["value"] == update_data["value"]

def test_delete_metric(client: TestClient, db: Session):
    # Create a metric first
    metric = MetricModel(
        project_id=1,
        name="To Be Deleted",
        value=100.0
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)

    response = client.delete(f"/api/metrics/{metric.id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/metrics/{metric.id}")
    assert get_response.status_code == 404 