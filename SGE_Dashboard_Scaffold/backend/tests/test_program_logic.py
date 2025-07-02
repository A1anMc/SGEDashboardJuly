import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.program_logic import ProgramLogic as ProgramLogicModel
from app.schemas.program_logic import ProgramLogicCreate

def test_create_program_logic(client: TestClient, db: Session):
    logic_data = {
        "project_id": 1,
        "input": "Test Input",
        "output": "Test Output",
        "outcome": "Test Outcome",
        "impact": "Test Impact"
    }
    response = client.post("/api/program-logic/", json=logic_data)
    assert response.status_code == 201
    data = response.json()
    assert data["input"] == logic_data["input"]
    assert data["output"] == logic_data["output"]
    assert data["id"]

def test_read_program_logic(client: TestClient, db: Session):
    # Create a program logic entry first
    program_logic = ProgramLogicModel(
        project_id=1,
        input="Test Input",
        output="Test Output",
        outcome="Test Outcome",
        impact="Test Impact"
    )
    db.add(program_logic)
    db.commit()
    db.refresh(program_logic)

    response = client.get(f"/api/program-logic/{program_logic.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["input"] == "Test Input"
    assert data["id"] == program_logic.id

def test_read_program_logic_by_project(client: TestClient, db: Session):
    # Create multiple program logic entries for the same project
    project_id = 1
    for i in range(3):
        program_logic = ProgramLogicModel(
            project_id=project_id,
            input=f"Input {i}",
            output=f"Output {i}",
            outcome=f"Outcome {i}",
            impact=f"Impact {i}"
        )
        db.add(program_logic)
    db.commit()

    response = client.get(f"/api/program-logic/project/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(pl["project_id"] == project_id for pl in data)

def test_read_nonexistent_program_logic(client: TestClient):
    response = client.get("/api/program-logic/999")
    assert response.status_code == 404

def test_update_program_logic(client: TestClient, db: Session):
    # Create a program logic entry first
    program_logic = ProgramLogicModel(
        project_id=1,
        input="Original Input",
        output="Original Output",
        outcome="Original Outcome",
        impact="Original Impact"
    )
    db.add(program_logic)
    db.commit()
    db.refresh(program_logic)

    update_data = {
        "input": "Updated Input",
        "impact": "Updated Impact"
    }
    response = client.put(f"/api/program-logic/{program_logic.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["input"] == update_data["input"]
    assert data["impact"] == update_data["impact"]
    assert data["output"] == "Original Output"  # Unchanged field

def test_delete_program_logic(client: TestClient, db: Session):
    # Create a program logic entry first
    program_logic = ProgramLogicModel(
        project_id=1,
        input="To Be Deleted",
        output="Output",
        outcome="Outcome",
        impact="Impact"
    )
    db.add(program_logic)
    db.commit()
    db.refresh(program_logic)

    response = client.delete(f"/api/program-logic/{program_logic.id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/program-logic/{program_logic.id}")
    assert get_response.status_code == 404 