import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi_utils.tasks import repeat_every
from dotenv import load_dotenv

from app.routers import grants, metrics, program_logic, projects, team
from app.services.scrapers import business_gov, community_grants, grantconnect, grants_gov
from app.core.config import settings
from app.core.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Shadow Goose Entertainment Dashboard API",
    description="Backend API for managing media projects, grants, and impact metrics.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with prefixes and tags
app.include_router(grants.router, prefix="/api/grants", tags=["Grants"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(program_logic.router, prefix="/api/program-logic", tags=["Program Logic"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(team.router, prefix="/api/team", tags=["Team"])

# Scheduled Tasks
@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 24)  # Run once per day
async def scrape_grants() -> None:
    """
    Scheduled job to scrape grants from various sources.
    Runs once per day and updates the database with new grants.
    """
    try:
        logger.info("Starting daily grant scraping job")
        
        # Run all scrapers concurrently
        scrapers = [
            business_gov.scrape_grants(),
            community_grants.scrape_grants(),
            grantconnect.scrape_grants(),
            grants_gov.scrape_grants()
        ]
        
        # Gather results
        results = await asyncio.gather(*scrapers, return_exceptions=True)
        
        # Log results
        for scraper, result in zip(['business.gov.au', 'community_grants', 'grantconnect', 'grants.gov'], results):
            if isinstance(result, Exception):
                logger.error(f"Error in {scraper} scraper: {str(result)}")
            else:
                logger.info(f"Successfully scraped {len(result)} grants from {scraper}")
                
        logger.info("Completed daily grant scraping job")
        
    except Exception as e:
        logger.error(f"Error in grant scraping job: {str(e)}")

# Error Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors in requests"""
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error"
        }
    )

# Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their processing time"""
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    logger.info(
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Status: {response.status_code} "
        f"Process Time: {process_time:.2f}ms"
    )
    
    return response

# Health Check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the Shadow Goose Entertainment API!",
        "docs_url": "/docs",
        "version": app.version
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 