from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case

from app.core.deps import get_db
from app.models.scraper_log import ScraperLog
from app.schemas.scraper_log import ScraperLog as ScraperLogSchema

router = APIRouter()

@router.get("/sources", response_model=List[dict])
def get_scraper_sources(db: Session = Depends(get_db)):
    """Get status of all scraper sources with their latest run statistics."""
    
    # Get the latest log entry for each source
    latest_logs = (
        db.query(
            ScraperLog.source_name,
            ScraperLog.status,
            func.max(ScraperLog.start_time).label("last_run"),
            func.avg(ScraperLog.duration_seconds).label("avg_duration"),
            func.sum(ScraperLog.grants_found).label("total_grants_found"),
            func.sum(ScraperLog.grants_added).label("total_grants_added"),
            func.sum(ScraperLog.grants_updated).label("total_grants_updated"),
            func.count(ScraperLog.id).label("total_runs"),
            func.sum(case((ScraperLog.status == 'error', 1), else_=0)).label("error_count")
        )
        .group_by(ScraperLog.source_name)
        .all()
    )
    
    return [
        {
            "source_name": log.source_name,
            "status": log.status,
            "last_run": log.last_run,
            "avg_duration_seconds": round(float(log.avg_duration), 2) if log.avg_duration else None,
            "total_grants_found": log.total_grants_found,
            "total_grants_added": log.total_grants_added,
            "total_grants_updated": log.total_grants_updated,
            "total_runs": log.total_runs,
            "error_rate": round((log.error_count / log.total_runs) * 100, 2) if log.total_runs > 0 else 0
        }
        for log in latest_logs
    ]

@router.get("/sources/{source_name}/history", response_model=List[ScraperLogSchema])
def get_source_history(source_name: str, limit: int = 10, db: Session = Depends(get_db)):
    """Get detailed history of a specific scraper source."""
    
    logs = (
        db.query(ScraperLog)
        .filter(ScraperLog.source_name == source_name)
        .order_by(desc(ScraperLog.start_time))
        .limit(limit)
        .all()
    )
    
    if not logs:
        raise HTTPException(status_code=404, detail=f"No logs found for source: {source_name}")
    
    return logs 