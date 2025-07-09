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

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 15 or higher (or Supabase account)
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/A1anMc/SGEDashboardJuly.git
cd SGEDashboardJuly
```

2. Install backend dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
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

### Starting the Development Servers

1. Start the backend server:
```bash
uvicorn app.main:app --reload
```

2. Start the frontend server:
```bash
cd frontend
npm run dev
```

## Development

- Frontend runs on `http://localhost:3000`
- Backend API runs on `http://localhost:8000`
- API documentation available at `http://localhost:8000/docs`

### VSCode Setup

Recommended extensions:
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- GitLens

## Project Structure

The project is organized into the following main directories:

* `/app` - Main FastAPI backend application
* `/frontend` - Next.js frontend application
* `/tests` - Backend test suite
* `/docs` - Project documentation

## Overview

The Shadow Goose Entertainment Dashboard is a centralized platform designed to streamline operations for media projects. It provides robust tools for tracking project progress, mapping program logic against the Impact Compass framework, discovering and managing Australian grant opportunities, and visualizing key impact metrics. This dashboard aims to enhance efficiency and provide clear insights into project performance and funding avenues.

## Error Handling

The SGE Dashboard implements a comprehensive error handling system. For detailed information, see:

- [Error Handling Architecture](docs/architecture/error-handling.md) - System design and implementation details
- [Error Handling Guidelines](docs/CONTRIBUTING.md#error-handling-guidelines) - Guidelines for contributors
- [Error Handling Examples](README.dev.md#error-handling) - Code examples and best practices

## License

This project is private and confidential.
