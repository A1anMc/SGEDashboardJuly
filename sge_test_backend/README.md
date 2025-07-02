# SGE Dashboard Backend

A FastAPI backend service for managing grants and automated scraping for the Shadow Goose Entertainment Dashboard.

## 🚀 Quick Start

1. **Setup Environment**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

2. **Configure Database**
```bash
# Apply database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 Features

### Core Infrastructure
- ✅ FastAPI with automatic OpenAPI docs
- ✅ SQLite database (ready for Supabase migration)
- ✅ Alembic migrations
- ✅ Environment-based configuration
- ✅ CORS configuration

### API Endpoints
- ✅ `/api/v1/grants`
  - List with filtering & pagination
  - Create, read, update, delete
  - Tag management
  - Status updates
- ✅ `/api/v1/scraper`
  - Manual scrape trigger
  - Background job processing

### Data Models
- ✅ Grants
  - Title, description, source
  - Deadline tracking
  - Tag management
  - Status workflow
  - Notes and timestamps
- ✅ Pydantic schemas
  - Request/response validation
  - API documentation

### Scraper Framework
- ✅ Base scraper class
- ⚠️ Source-specific scrapers (templates ready)
  - Business.gov.au
  - GrantConnect
  - Community Grants

## 🏗 Project Structure

```
sge_test_backend/
├── app/
│   ├── api/               # API endpoints
│   │   └── v1/
│   │       ├── grants.py  # Grant CRUD operations
│   │       └── scraper.py # Scraper endpoints
│   ├── core/              # Core config
│   │   ├── config.py     # Environment settings
│   │   └── deps.py       # Dependencies
│   ├── db/               # Database setup
│   │   ├── base.py       # SQLAlchemy setup
│   │   └── session.py    # DB session
│   ├── models/           # SQLAlchemy models
│   │   ├── grant.py      # Grant model
│   │   └── user.py       # User model
│   ├── schemas/          # Pydantic schemas
│   │   └── grant.py      # Grant schemas
│   └── services/         # Business logic
│       └── scrapers/     # Grant scrapers
├── tests/                # Test suite
├── alembic/              # DB migrations
├── .env.example         # Environment template
└── requirements.txt     # Dependencies
```

## 🔧 Development

### Environment Variables
Create a `.env` file with:

```env
# Required
DATABASE_URL=sqlite:///./sge.db
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-here

# Optional
LOG_LEVEL=INFO
ENABLE_DOCS=true
```

### API Documentation
The API documentation is available at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### Grant Endpoints

**List Grants**
```http
GET /api/v1/grants?status=open&tags=research,science
```

**Create Grant**
```http
POST /api/v1/grants
Content-Type: application/json

{
    "title": "Research Grant 2024",
    "description": "Research funding opportunity",
    "deadline": "2024-12-31T23:59:59",
    "tags": ["research", "science"],
    "status": "open",
    "source": "GrantConnect"
}
```

**Update Grant**
```http
PUT /api/v1/grants/{id}
Content-Type: application/json

{
    "status": "closed"
}
```

### Database Management
```bash
# Create new migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_grants.py
```

## 📋 Development Tasks

### In Progress
- [ ] Source-specific scraper implementations
- [ ] User authentication
- [ ] Test coverage
- [ ] Scheduled scraping jobs

### Completed
- [x] Project structure
- [x] Database models
- [x] API endpoints
- [x] Migration system
- [x] CORS configuration
- [x] Scraper framework
- [x] Error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/name`)
3. Make your changes
4. Run tests (`pytest`)
5. Submit a pull request

## 📝 License

This project is proprietary and confidential.
© 2024 Shadow Goose Entertainment