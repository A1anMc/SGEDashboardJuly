# Development Guide

This guide covers setting up and developing the SGE Dashboard locally.

## 🛠️ Local Development Setup

### Prerequisites

- **Node.js**: 18+ (recommended: 20+)
- **Python**: 3.8+ (recommended: 3.11+)
- **PostgreSQL**: 15+ (or use Docker)
- **Git**: Latest version
- **npm** or **yarn**: Package managers

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd sge-dashboard

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Frontend Setup
cd ../frontend
npm install
```

### Environment Configuration

#### Backend Environment (`.env`)
```env
# Development Settings
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sge_dashboard_dev

# Security
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-change-in-production

# CORS
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

#### Frontend Environment (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
NEXT_PUBLIC_ENV=development
```

### Starting Development Servers

#### Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Server
```bash
cd frontend
npm run dev
```

### Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Project Structure

```
sge-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/     # API endpoints
│   │   │       └── api.py         # API router
│   │   ├── core/                  # Core configuration
│   │   ├── db/                    # Database setup
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/              # Business logic
│   │   └── main.py               # FastAPI app
│   ├── alembic/                   # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js app router
│   │   │   ├── dashboard/        # Dashboard pages
│   │   │   └── layout.tsx        # Root layout
│   │   ├── components/           # React components
│   │   ├── services/             # API services
│   │   ├── hooks/                # Custom hooks
│   │   ├── types/                # TypeScript types
│   │   └── utils/                # Utility functions
│   ├── public/                   # Static assets
│   └── package.json
└── docs/                         # Documentation
```

## 🔧 Development Tools

### VS Code Extensions (Recommended)

#### Python
- Python
- Pylance
- Python Docstring Generator
- Python Test Explorer

#### JavaScript/TypeScript
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript Importer

#### General
- GitLens
- Git History
- Auto Rename Tag
- Bracket Pair Colorizer

### Useful Commands

#### Backend
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Format code
black app/
isort app/

# Lint code
ruff check app/
```

#### Frontend
```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Type checking
npm run type-check

# Lint code
npm run lint

# Format code
npm run format
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
pytest tests/ -v --tb=short
pytest tests/ -k "test_function_name"
```

### Frontend Testing
```bash
cd frontend
npm test
npm test -- --watch
npm test -- --coverage
```

## 🗄️ Database

### Local Database Setup

#### Using PostgreSQL
```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu

# Create database
createdb sge_dashboard_dev

# Run migrations
cd backend
alembic upgrade head
```

#### Using Docker
```bash
# Start PostgreSQL container
docker run --name sge-postgres \
  -e POSTGRES_DB=sge_dashboard_dev \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Run migrations
cd backend
alembic upgrade head
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🔍 Debugging

### Backend Debugging
```python
# Add debug prints
print(f"Debug: {variable}")

# Use Python debugger
import pdb; pdb.set_trace()

# Use logging
import logging
logging.debug(f"Debug message: {variable}")
```

### Frontend Debugging
```javascript
// Console logging
console.log('Debug:', variable);

// React DevTools
// Install React Developer Tools browser extension

// Next.js debugging
// Check .next/server/pages-manifest.json for routing issues
```

## 📦 Package Management

### Backend Dependencies
```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Frontend Dependencies
```bash
# Install new package
npm install package-name

# Install dev dependency
npm install --save-dev package-name

# Update packages
npm update
npm audit fix
```

## 🚀 Performance

### Backend Performance
- Use async/await for database operations
- Implement connection pooling
- Add caching where appropriate
- Monitor query performance

### Frontend Performance
- Use React.memo for expensive components
- Implement code splitting
- Optimize bundle size
- Use Next.js Image component

## 🔒 Security

### Development Security
- Never commit secrets to version control
- Use environment variables for sensitive data
- Validate all user inputs
- Implement proper authentication

### Security Best Practices
- Keep dependencies updated
- Use HTTPS in production
- Implement rate limiting
- Add security headers

## 📚 Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - Database management
- [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi) - React debugging 