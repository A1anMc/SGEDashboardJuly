# 🧱 Architecture Overview

## System Map

```
Frontend (Next.js 14.0.0 + Tailwind)
  ↕ API (FastAPI @ localhost:8000)
    ↕ Database (SQLite/PostgreSQL)
    ↕ Scraper Services (aiohttp + BeautifulSoup)
    ↕ Tag System
```

## Components
- Frontend: 
  - UI Components (React + TypeScript)
  - Tailwind CSS for styling
  - API Client Services
  - Component Testing (Jest)
- Backend: 
  - FastAPI Routers (grants, tasks, tags, comments)
  - SQLAlchemy Models
  - Async Scraper Services
  - Authentication System
- Database: 
  - SQLite for Development
  - PostgreSQL for Production
  - Alembic Migrations
- Testing:
  - Frontend: Jest + React Testing Library
  - Backend: pytest
  - API: Postman Collections

## Data Flow
1. User Interface Layer
   - Next.js Pages and Components
   - Form Handling and Validation
   - Real-time Updates
2. API Layer
   - RESTful Endpoints
   - JWT Authentication
   - Request Validation
3. Service Layer
   - Business Logic
   - Data Processing
   - External Integrations
4. Data Layer
   - Database Operations
   - Caching (if implemented)
   - Data Migrations

## Current Features
- Grant Management System
- Task Tracking
- Tag System
- Comment Threading
- User Authentication

## Documentation Map
- Task Management: See `task_management.md`
- Project Planning: See `plan.md`
- Development Timeline: See `roadmap.md`
- Strategic Overview: See `strategic_handoff.md`
