from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import grants, metrics, program_logic

app = FastAPI(
    title="Shadow Goose Entertainment Dashboard API",
    description="Backend API for managing media projects, grants, and impact metrics.",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(grants.router, prefix="/api/grants", tags=["Grants"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(program_logic.router, prefix="/api/program-logic", tags=["Program Logic"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Shadow Goose Entertainment API!",
        "docs_url": "/docs",
        "version": app.version
    } 