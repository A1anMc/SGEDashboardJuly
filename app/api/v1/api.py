from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, projects, tasks, grants, tags, scraper_status, comments, health

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(grants.router, prefix="/grants", tags=["grants"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(scraper_status.router, prefix="/scraper", tags=["scraper"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(health.router, tags=["health"]) 