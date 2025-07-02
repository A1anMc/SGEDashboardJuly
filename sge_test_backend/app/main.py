from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import grants, scraper

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    grants.router,
    prefix=f"{settings.API_V1_PREFIX}/grants",
    tags=["grants"]
)
app.include_router(
    scraper.router,
    prefix=f"{settings.API_V1_PREFIX}/scraper",
    tags=["scraper"]
)

@app.get("/health")
def health_check():
    return {"status": "healthy"} 