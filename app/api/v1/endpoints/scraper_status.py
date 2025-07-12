from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case

from app.core.deps import get_db
from app.models.scraper_log import ScraperLog
from app.schemas.scraper_log import ScraperLog as ScraperLogSchema

router = APIRouter()

@router.get("/status")
def get_scraper_status(db: Session = Depends(get_db)):
    """Get overall scraper status and available sources."""
    
    # Get available sources from the latest logs
    latest_logs = (
        db.query(
            ScraperLog.source_name,
            ScraperLog.status,
            func.max(ScraperLog.start_time).label("last_run"),
        )
        .group_by(ScraperLog.source_name)
        .all()
    )
    
    # Default available sources if no logs exist
    available_sources = ["business_gov", "grantconnect", "australian_grants"]
    
    if latest_logs:
        available_sources = [log.source_name for log in latest_logs]
    
    return {
        "status": "ready",
        "available_sources": available_sources,
        "total_sources": len(available_sources),
        "last_run": latest_logs[0].last_run if latest_logs else None
    }

@router.post("/run")
def run_scrapers(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run all available scrapers."""
    
    # For now, return a success response
    # In a full implementation, this would trigger actual scraping
    return {
        "status": "started",
        "message": "Scraper run initiated",
        "available_sources": ["business_gov", "grantconnect", "australian_grants"]
    }

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