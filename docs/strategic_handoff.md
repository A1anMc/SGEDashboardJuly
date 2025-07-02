# Shadow Goose Entertainment Dashboard - Strategic Documentation Pack

## 1. Project Status Overview

### Current State
The Shadow Goose Entertainment (SGE) Dashboard is entering Phase 3 of development, focusing on Grant Management capabilities. This phase aims to streamline the discovery and management of grant opportunities for media projects.

### Current Phase (Phase 3 - Grant Management)
- 🔄 Grant model implementation
- 🔄 Grant discovery interface
- 🔄 Scraper integration
- 🔄 Grant matching algorithm

### Tech Stack
- **Frontend:**
  - Next.js 14 with App Router
  - TypeScript
  - Tailwind CSS
  - Headless UI
  - React Query

- **Backend:**
  - FastAPI
  - Python 3.11+
  - SQLAlchemy ORM
  - Alembic Migrations
  - PostgreSQL (via Supabase)

- **Infrastructure:**
  - Database: Supabase (PostgreSQL)
  - Backend Hosting: Render
  - Frontend Hosting: Vercel
  - File Storage: Supabase Storage

## 2. Project Structure

```
/
├── app/                    # Backend application
│   ├── api/               # API endpoints
│   ├── core/              # Core configurations
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models
│   ├── routers/           # FastAPI routers
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic
├── frontend/              # Next.js frontend
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── lib/             # Utility functions
│   └── styles/          # CSS styles
├── tests/                # Test suites
├── docs/                 # Documentation
└── alembic/              # Database migrations
```

## 3. Initial Database Schema

### Core Models

#### Grant
```sql
- id: Integer (PK)
- title: String
- description: Text
- source: String
- deadline: DateTime
- tags: String
- status: String
- notes: Text
- created_at: DateTime
- updated_at: DateTime
```

#### User
```sql
- id: Integer (PK)
- email: String (unique)
- hashed_password: String
- full_name: String
- is_active: Boolean
- is_superuser: Boolean
- created_at: DateTime
- updated_at: DateTime
```

### Initial Relationships
- User → Grants (Many-to-Many, for tracking)
- Grant → Tags (One-to-Many)

## 4. Phase 3 API Endpoints

### Grant Management
```
GET /api/grants/                # List all grants
POST /api/grants/               # Create new grant
GET /api/grants/{id}           # Get grant details
PUT /api/grants/{id}           # Update grant
DELETE /api/grants/{id}        # Delete grant
GET /api/grants/scrape         # Trigger grant scraping
GET /api/grants/match          # Get matching grants
```

### Authentication (Required for Grant Access)
```
POST /api/auth/login
POST /api/auth/register
GET /api/auth/me
```

## 5. Phase 3 Development Plan

### Now (Active Development)
- 🔄 Setting up grant database schema
- 🔄 Implementing basic CRUD operations
- 🔄 Building scraper framework
- 🔄 Creating grant discovery interface

### Next (Short-term)
- 📅 Grant matching algorithm
- 📊 Grant analytics dashboard
- 🔔 Grant deadline notifications

### Later (Future Phases)
- 🌐 Extended grant sources
- 📱 Mobile grant viewing
- 🤖 AI-powered grant recommendations

## 6. Testing Strategy

### Current Focus
- Unit tests for grant model
- Integration tests for scraper
- API endpoint testing
- Grant matching algorithm validation

### Test Locations
- `/tests/models/test_grants.py`
- `/tests/api/test_grants.py`
- `/tests/services/test_scraper.py`

## 7. Initial Deployment

### Development Environment
- Backend: Render (development instance)
- Frontend: Vercel (preview deployments)
- Database: Supabase (development instance)

### Planned Jobs
- Daily grant scraping
- Weekly grant matches
- Grant deadline notifications

## 8. Next Steps

### Immediate Tasks
1. Complete grant model implementation
2. Set up initial scraper for one source
3. Create basic grant listing interface
4. Implement simple matching logic

### Technical Considerations
1. Data structure for efficient grant matching
2. Scraper reliability and error handling
3. Grant data validation rules
4. API rate limiting for scrapers

### Risk Areas
1. Grant data accuracy
2. Scraper maintenance
3. Match algorithm performance
4. Data storage scaling 