# SGE Dashboard - Setup Guide

## Fixed Issues

The following communication issues between frontend and backend have been resolved:

### 1. **API Path Mismatch** ✅
- **Problem**: Frontend was calling `/api/` endpoints, but backend expected `/api/v1/`
- **Fix**: Updated all API calls in `frontend/src/services/api.ts` to use `/api/v1/` prefix

### 2. **Missing Dependencies** ✅
- **Problem**: Frontend package.json was missing `axios` and other required dependencies
- **Fix**: Added all missing dependencies including:
  - `axios` for API calls
  - `@radix-ui/*` components for UI
  - `class-variance-authority`, `clsx`, `tailwind-merge` for styling
  - `lucide-react` for icons
  - Testing libraries

### 3. **Missing API Routers** ✅
- **Problem**: Frontend expected `/users` and `/projects` APIs but routers didn't exist
- **Fix**: Created new routers:
  - `app/routers/users.py` - User management endpoints
  - `app/routers/projects.py` - Project CRUD operations
  - `app/schemas/user.py` - User response schemas
  - `app/schemas/project.py` - Project schemas
  - Updated `app/main.py` to include new routers

### 4. **Backend Router Registration** ✅
- **Problem**: Existing `grants.py` and `tags.py` routers weren't imported in main.py
- **Fix**: Added missing router imports to `app/main.py`

## How to Run Locally

### Option 1: Using the Startup Script (Recommended)

1. **Install Backend Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies** (already done):
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Run Both Servers**:
   ```bash
   ./start_dev.sh
   ```

This will start both servers and show you the URLs:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

1. **Terminal 1 - Backend**:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Terminal 2 - Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

## Available API Endpoints

The backend now provides the following API endpoints:

### Tasks
- `GET /api/v1/tasks` - List all tasks
- `POST /api/v1/tasks` - Create a task
- `GET /api/v1/tasks/{id}` - Get specific task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### Users
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{id}` - Get specific user

### Projects
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create a project
- `GET /api/v1/projects/{id}` - Get specific project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Grants
- `GET /api/v1/grants` - List all grants
- `POST /api/v1/grants` - Create a grant
- `GET /api/v1/grants/{id}` - Get specific grant
- `PUT /api/v1/grants/{id}` - Update grant
- `DELETE /api/v1/grants/{id}` - Delete grant

### Tags
- `GET /api/v1/tags` - List all tags
- `POST /api/v1/tags` - Create a tag
- `GET /api/v1/tags/{id}` - Get specific tag
- `PUT /api/v1/tags/{id}` - Update tag
- `DELETE /api/v1/tags/{id}` - Delete tag

### Comments
- `GET /api/v1/comments` - List comments
- `POST /api/v1/comments` - Create a comment
- `PUT /api/v1/comments/{id}` - Update comment
- `DELETE /api/v1/comments/{id}` - Delete comment

## Configuration

### Backend Configuration
- **Host**: 0.0.0.0
- **Port**: 8000
- **CORS**: Configured for `http://localhost:3000`
- **Database**: SQLite (`app.db`)

### Frontend Configuration
- **Port**: 3000
- **API Base URL**: `http://localhost:8000`
- **Framework**: Next.js 14

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   - Backend: Kill process using port 8000: `lsof -ti:8000 | xargs kill -9`
   - Frontend: Kill process using port 3000: `lsof -ti:3000 | xargs kill -9`

2. **Database Issues**:
   - Delete `app.db` and restart backend to create fresh database
   - Run migrations: `alembic upgrade head`

3. **CORS Errors**:
   - Ensure backend is running on port 8000
   - Check that `http://localhost:3000` is in CORS_ORIGINS

4. **API Not Found (404)**:
   - Verify API calls use `/api/v1/` prefix
   - Check that all routers are imported in `app/main.py`

5. **Authentication Issues**:
   - Most endpoints require authentication
   - Check that JWT tokens are properly handled

### Checking Backend Health

Visit http://localhost:8000/docs to see the auto-generated API documentation and test endpoints.

### Checking Frontend Health

Visit http://localhost:3000 to see the frontend application.

## Next Steps

1. **Database Setup**: Initialize with sample data
2. **Authentication**: Set up user registration/login
3. **Environment Variables**: Configure for production
4. **Testing**: Run test suites for both frontend and backend

## Files Changed

- `frontend/package.json` - Added missing dependencies
- `frontend/src/services/api.ts` - Fixed API paths
- `app/main.py` - Added missing router imports
- `app/routers/users.py` - New user router
- `app/routers/projects.py` - New project router
- `app/schemas/user.py` - New user schemas
- `app/schemas/project.py` - New project schemas
- `requirements.txt` - Added email validation
- `start_dev.sh` - New startup script