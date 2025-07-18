# Architecture Overview

This document provides an overview of the SGE Dashboard architecture and system design.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│                 │    │                 │    │                 │
│ • React         │    │ • FastAPI       │    │ • PostgreSQL    │
│ • TypeScript    │    │ • SQLAlchemy    │    │ • Alembic       │
│ • Tailwind CSS  │    │ • Pydantic      │    │ • Connection    │
│ • TanStack Query│    │ • JWT Auth      │    │   Pooling       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Deployment    │    │   Monitoring    │    │   External      │
│   (Render)      │    │   (Health       │    │   Services      │
│                 │    │    Checks)      │    │                 │
│ • Auto-scaling  │    │ • Uptime        │    │ • Email Service │
│ • SSL/TLS       │    │ • Performance   │    │ • File Storage  │
│ • CDN           │    │ • Error Tracking│    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Design Principles

### 1. **Separation of Concerns**
- Frontend handles UI/UX and client-side logic
- Backend manages business logic and data persistence
- Database stores data with proper relationships

### 2. **API-First Design**
- RESTful API with consistent patterns
- JSON-based communication
- Proper HTTP status codes and error handling

### 3. **Scalability**
- Stateless backend design
- Connection pooling for database
- Auto-scaling on Render

### 4. **Security**
- JWT-based authentication
- CORS protection
- Input validation and sanitization
- HTTPS enforcement

## 🏛️ Backend Architecture

### FastAPI Application Structure

```
app/
├── main.py                 # FastAPI app entry point
├── core/                   # Core configuration
│   ├── config.py          # Settings and environment
│   ├── security.py        # Authentication & authorization
│   └── deps.py            # Dependency injection
├── api/                    # API layer
│   └── v1/
│       ├── api.py         # API router
│       └── endpoints/     # Route handlers
├── models/                 # Database models
│   ├── user.py            # User model
│   ├── grant.py           # Grant model
│   └── task.py            # Task model
├── schemas/                # Pydantic schemas
│   ├── user.py            # User schemas
│   ├── grant.py           # Grant schemas
│   └── task.py            # Task schemas
├── services/               # Business logic
│   ├── auth.py            # Authentication service
│   ├── grants.py          # Grant management
│   └── tasks.py           # Task management
└── db/                     # Database layer
    ├── base.py            # Database setup
    ├── session.py         # Session management
    └── init_db.py         # Database initialization
```

### Key Components

#### 1. **FastAPI Application**
- High-performance async web framework
- Automatic API documentation
- Built-in validation and serialization

#### 2. **SQLAlchemy ORM**
- Database abstraction layer
- Migration support with Alembic
- Connection pooling for performance

#### 3. **Pydantic Models**
- Data validation and serialization
- Automatic API documentation
- Type safety and IDE support

#### 4. **JWT Authentication**
- Stateless authentication
- Token-based session management
- Secure password hashing

## 🎨 Frontend Architecture

### Next.js Application Structure

```
src/
├── app/                    # App Router (Next.js 13+)
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── dashboard/         # Dashboard routes
│       ├── layout.tsx     # Dashboard layout
│       ├── page.tsx       # Dashboard home
│       ├── grants/        # Grant pages
│       ├── tasks/         # Task pages
│       └── settings/      # Settings pages
├── components/             # React components
│   ├── layout/            # Layout components
│   ├── grants/            # Grant components
│   ├── tasks/             # Task components
│   └── ui/                # UI components
├── services/               # API services
│   ├── api.ts             # API client
│   ├── grants.ts          # Grant API calls
│   └── tasks.ts           # Task API calls
├── hooks/                  # Custom React hooks
│   ├── useGrants.ts       # Grant data hooks
│   └── useTasks.ts        # Task data hooks
├── types/                  # TypeScript types
│   ├── api.ts             # API types
│   └── models.ts          # Data models
└── utils/                  # Utility functions
    ├── error-handling.ts  # Error handling
    └── utils.ts           # General utilities
```

### Key Components

#### 1. **Next.js App Router**
- File-based routing
- Server and client components
- Built-in optimizations

#### 2. **React Components**
- Functional components with hooks
- Component composition
- Reusable UI components

#### 3. **TanStack Query**
- Server state management
- Caching and synchronization
- Optimistic updates

#### 4. **Tailwind CSS**
- Utility-first CSS framework
- Responsive design
- Custom design system

## 🗄️ Database Architecture

### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grants table
CREATE TABLE grants (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    amount DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'active',
    deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    assigned_to INTEGER REFERENCES users(id),
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tags table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6',
    parent_id INTEGER REFERENCES tags(id)
);

-- Many-to-many relationships
CREATE TABLE grant_tags (
    grant_id INTEGER REFERENCES grants(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (grant_id, tag_id)
);
```

### Database Design Principles

#### 1. **Normalization**
- Proper table relationships
- Avoid data redundancy
- Maintain data integrity

#### 2. **Indexing**
- Primary key indexes
- Foreign key indexes
- Search field indexes

#### 3. **Constraints**
- NOT NULL constraints
- UNIQUE constraints
- Foreign key constraints

## 🔄 Data Flow

### 1. **User Authentication Flow**
```
User Login → Frontend → Backend API → Database → JWT Token → Frontend Storage
```

### 2. **Data Fetching Flow**
```
Frontend Request → TanStack Query → API Service → Backend API → Database → Response → Cache → UI Update
```

### 3. **Data Mutation Flow**
```
User Action → Frontend → API Service → Backend API → Database → Response → Cache Invalidation → UI Update
```

## 🔒 Security Architecture

### Authentication & Authorization

#### 1. **JWT Tokens**
- Access tokens with expiration
- Refresh token mechanism
- Secure token storage

#### 2. **Password Security**
- bcrypt hashing
- Salt generation
- Secure comparison

#### 3. **CORS Protection**
- Origin validation
- Method restrictions
- Header controls

### Data Protection

#### 1. **Input Validation**
- Pydantic schemas
- SQL injection prevention
- XSS protection

#### 2. **Output Sanitization**
- HTML encoding
- JSON escaping
- Content-Type headers

## 📊 Performance Architecture

### Backend Performance

#### 1. **Database Optimization**
- Connection pooling
- Query optimization
- Index strategy

#### 2. **Caching Strategy**
- Response caching
- Database query caching
- Static asset caching

#### 3. **Async Processing**
- Non-blocking I/O
- Background tasks
- Queue management

### Frontend Performance

#### 1. **Code Splitting**
- Route-based splitting
- Component lazy loading
- Bundle optimization

#### 2. **Caching Strategy**
- Browser caching
- Service worker caching
- API response caching

#### 3. **Optimization**
- Image optimization
- Font loading
- Critical CSS

## 🔍 Monitoring & Observability

### Health Checks
- Backend health endpoint
- Frontend health check
- Database connectivity

### Logging
- Structured logging
- Error tracking
- Performance monitoring

### Metrics
- Response times
- Error rates
- Resource usage

## 🚀 Deployment Architecture

### Render Platform

#### 1. **Backend Service**
- Python environment
- Gunicorn WSGI server
- Auto-scaling configuration

#### 2. **Frontend Service**
- Node.js environment
- Next.js standalone build
- Static asset serving

#### 3. **Database**
- PostgreSQL service
- Automated backups
- Connection pooling

### CI/CD Pipeline

#### 1. **GitHub Integration**
- Automatic deployments
- Environment management
- Secret management

#### 2. **Build Process**
- Dependency installation
- Code compilation
- Asset optimization

#### 3. **Deployment Strategy**
- Blue-green deployment
- Rollback capability
- Health check validation

## 🔮 Future Architecture Considerations

### Scalability
- Microservices architecture
- Load balancing
- Database sharding

### Performance
- CDN integration
- Edge computing
- Real-time features

### Security
- OAuth integration
- Multi-factor authentication
- Audit logging

### Monitoring
- APM integration
- Custom dashboards
- Alert systems 