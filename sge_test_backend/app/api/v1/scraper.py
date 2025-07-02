from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.services.scrapers.scraper_service import run_all_scrapers

router = APIRouter()

@router.post("/run", status_code=202)
async def run_scraper(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> dict:
    """
    Trigger the grant scraper to run in the background.
    """
    background_tasks.add_task(run_all_scrapers, db)
    return {"message": "Scraper started successfully"} 