# Shadow Goose Entertainment Dashboard

A comprehensive grant management and project tracking system for the entertainment industry.

## Features

- **Grant Management**: Track and manage grant opportunities with automated scraping from multiple sources
- **Tag System**: Hierarchical tag management with synonyms for better organization
- **Project Tracking**: Monitor project progress and resource allocation
- **Task Management**: Organize and track tasks with priority and status tracking

## Tech Stack

- **Backend**: Python/FastAPI
- **Frontend**: Next.js/React with TypeScript
- **Database**: PostgreSQL
- **Authentication**: JWT-based auth system

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/A1anMc/SGEDashboardJuly.git
cd SGEDashboardJuly
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
alembic upgrade head
```

6. Start the development servers:

Backend:
```bash
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

## Development

- Frontend runs on `http://localhost:3000`
- Backend API runs on `http://localhost:8000`
- API documentation available at `http://localhost:8000/docs`

## License

This project is private and confidential.

## Overview

The Shadow Goose Entertainment Dashboard is a centralized platform designed to streamline operations for media projects. It provides robust tools for tracking project progress, mapping program logic against the Impact Compass framework, discovering and managing Australian grant opportunities, and visualizing key impact metrics. This dashboard aims to enhance efficiency and provide clear insights into project performance and funding avenues.

## Project Structure

The project is organized into the following main directories:

* `/app` - Main FastAPI backend application
* `/frontend` - Next.js frontend application
* `/tests` - Backend test suite
* `/docs` - Project documentation

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 15 or higher (or Supabase account)
- Git

### Environment Variables

Create two `.env` files:

1. Backend `.env` (in root directory):
```env
# Server
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sge_dashboard

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Authentication
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Airtable Integration
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id

# External APIs
BUSINESS_GOV_API_KEY=your_business_gov_api_key
GRANTS_GOV_API_KEY=your_grants_gov_api_key

# Logging
LOG_LEVEL=INFO
```

2. Frontend `.env.local` (in `/frontend` directory):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Backend Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Apply database migrations:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Development Environment

### VSCode Setup

Recommended extensions:
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- GitLens

### Code Style

- Backend: Follow PEP 8 guidelines
- Frontend: Use Prettier and ESLint configurations provided
- Git commits: Follow conventional commits format

### Code Quality Tools

- **Cleanup and Validation**
  ```bash
  # Install quality tools
  pip install vulture pytest pytest-cov pylint mypy

  # Run cleanup and validation
  python cleanup_and_validate.py

  # Additional validation
  pylint app/     # Syntax and style checking
  mypy app/      # Type checking
  ```
  This script:
  - Detects and removes unused code
  - Runs test coverage analysis
  - Enforces 90% minimum coverage
  - Validates syntax and imports
  - Checks API route usage
  - Analyzes dependencies
  - Generates comprehensive reports

- **Access Control**
  The system implements role-based access control with:
  - Owner: Full administrative rights
  - Assignee: Task execution rights
  - Follower: Update notifications
  - Observer: Read-only access
  See `docs/task_management.md` for detailed permissions.

## Deployment

### Backend Deployment (Render)

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your forked repository
4. Set environment variables
5. Deploy with the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)

1. Fork this repository
2. Create a new project on Vercel
3. Connect your forked repository
4. Set environment variables
5. Deploy with default settings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary and confidential. All rights reserved by Shadow Goose Entertainment.
© 2024 Shadow Goose Entertainment 