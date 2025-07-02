from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.metric import Metric as MetricModel
from app.schemas.metric import Metric, MetricCreate, MetricUpdate

router = APIRouter()

@router.get("/", response_model=List[Metric])
def get_metrics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve metrics with pagination.
    """
    metrics = db.query(MetricModel).offset(skip).limit(limit).all()
    return metrics

@router.post("/", response_model=Metric, status_code=status.HTTP_201_CREATED)
def create_metric(
    metric_in: MetricCreate,
    db: Session = Depends(get_db)
):
    """
    Create new metric.
    """
    metric = MetricModel(**metric_in.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric

@router.get("/{metric_id}", response_model=Metric)
def get_metric(
    metric_id: int,
    db: Session = Depends(get_db)
):
    """
    Get metric by ID.
    """
    metric = db.query(MetricModel).filter(MetricModel.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric

@router.get("/project/{project_id}", response_model=List[Metric])
def get_metrics_by_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all metrics for a specific project.
    """
    metrics = db.query(MetricModel).filter(MetricModel.project_id == project_id).all()
    return metrics

@router.put("/{metric_id}", response_model=Metric)
def update_metric(
    metric_id: int,
    metric_in: MetricUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a metric.
    """
    metric = db.query(MetricModel).filter(MetricModel.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    update_data = metric_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(metric, field, value)
    
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric

@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric(
    metric_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a metric.
    """
    metric = db.query(MetricModel).filter(MetricModel.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    db.delete(metric)
    db.commit()
    return None