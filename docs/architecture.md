# 🧱 Architecture Overview

## System Map

```
Frontend (Next.js + Tailwind @ Vercel)
  ↕ API (FastAPI @ Render)
    ↕ Database (SQLite/PostgreSQL)
    ↕ Scraper Services (Python + BeautifulSoup)
    ↕ Airtable (Metrics Sync)
```

## Components
- Frontend: UI Views, API Utility, Chart Components
- Backend: Routers, Services, Models, Task Management
- Database: SQL Tables (`projects`, `tasks`, `grants`, `metrics`, etc.)
- Deployment: Render (backend), Vercel (frontend)

## Data Flow
1. User enters/edits data (project, task, grant)
2. Backend stores it in database
3. Scrapers run daily and add new grants
4. Airtable form metrics sync via backend
5. Frontend fetches and visualises all data

## Documentation
- Task Management System: See `task_management.md`
- Project Planning: See `plan.md`
- Development Timeline: See `roadmap.md`
