# 🧱 Architecture Overview

## System Map

```
Frontend (Next.js 15 + Tailwind CSS)
  ↕ Direct API Calls
    ↕ Backend (FastAPI @ sge-dashboard-api.onrender.com)
      ↕ Database (PostgreSQL)
      ↕ Scraper Services (aiohttp + BeautifulSoup)
      ↕ Tag System
      ↕ Authentication (JWT)
```

## Components

### Frontend (Next.js 15)
- **UI Components**: React + TypeScript with Radix UI
- **Styling**: Tailwind CSS for responsive design
- **State Management**: TanStack Query for server state
- **API Integration**: Direct calls to backend API
- **Routing**: Next.js App Router with dashboard layout
- **Configuration**: Centralized config management

### Backend (FastAPI)
- **API Routes**: RESTful endpoints for all resources
- **Database**: SQLAlchemy ORM with PostgreSQL
- **Authentication**: JWT-based authentication system
- **Scrapers**: Async web scraping services
- **Validation**: Pydantic models for request/response validation
- **Security**: CORS, rate limiting, security headers

### Database (PostgreSQL)
- **Migrations**: Alembic for schema management
- **Models**: User, Grant, Task, Project, Tag, Comment
- **Relationships**: Proper foreign key constraints
- **Indexing**: Optimized for query performance

### External Services
- **Render**: Production hosting for both frontend and backend
- **PostgreSQL**: Managed database service
- **Scrapers**: External grant data sources

## Data Flow

### 1. User Interface Layer
- Next.js Pages and Components
- Form Handling and Validation
- Real-time Updates via TanStack Query
- Responsive Design with Tailwind CSS

### 2. API Layer
- RESTful Endpoints (`/api/v1/`)
- JWT Authentication
- Request/Response Validation
- Error Handling and Logging

### 3. Service Layer
- Business Logic Implementation
- Data Processing and Transformation
- External API Integrations
- Scraper Services

### 4. Data Layer
- Database Operations via SQLAlchemy
- Migration Management with Alembic
- Connection Pooling
- Data Integrity Constraints

## API Endpoints

### Core Resources
- `GET /api/v1/grants/` - List all grants
- `POST /api/v1/grants/` - Create new grant
- `GET /api/v1/grants/{id}/` - Get specific grant
- `PUT /api/v1/grants/{id}/` - Update grant
- `DELETE /api/v1/grants/{id}/` - Delete grant

### Task Management
- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/{id}/` - Get specific task
- `PUT /api/v1/tasks/{id}/` - Update task
- `DELETE /api/v1/tasks/{id}/` - Delete task

### User Management
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/{id}/` - Get specific user
- `PUT /api/v1/users/{id}/` - Update user

### System Health
- `GET /health` - Health check endpoint
- `GET /api/docs` - Interactive API documentation

## Current Features

### ✅ Implemented
- **Grant Management**: Full CRUD operations with search and filtering
- **Task Tracking**: Task creation, assignment, and status tracking
- **Tag System**: Flexible tagging for grants and tasks
- **Comment Threading**: Nested comments on tasks
- **User Authentication**: JWT-based authentication
- **Database Integration**: Full PostgreSQL integration
- **API Documentation**: Auto-generated OpenAPI docs
- **Health Monitoring**: Comprehensive health checks

### 🚧 In Development
- **Advanced Search**: Full-text search capabilities
- **Reporting**: Analytics and reporting features
- **Notifications**: Real-time notifications
- **File Uploads**: Document and media uploads

## Security Architecture

### Authentication
- JWT tokens for stateless authentication
- Token refresh mechanism
- Secure password hashing

### Authorization
- Role-based access control (RBAC)
- Resource-level permissions
- API endpoint protection

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

### Infrastructure Security
- HTTPS enforcement
- Security headers
- Rate limiting
- CORS configuration

## Performance Considerations

### Frontend
- Code splitting and lazy loading
- Image optimization
- Caching strategies
- Bundle size optimization

### Backend
- Database query optimization
- Connection pooling
- Caching layers
- Async processing

### Database
- Proper indexing
- Query optimization
- Connection management
- Migration strategies

## Monitoring and Logging

### Application Monitoring
- Health check endpoints
- Performance metrics
- Error tracking
- User analytics

### Infrastructure Monitoring
- Service availability
- Resource utilization
- Response times
- Error rates

## Documentation Map
- **Task Management**: See `task_management.md`
- **Project Planning**: See `plan.md`
- **Development Timeline**: See `roadmap.md`
- **Strategic Overview**: See `strategic_handoff.md`
- **API Documentation**: See `docs/api/README.md`
- **Deployment Guide**: See `docs/deployment/README.md`
