# API Documentation

This document provides comprehensive information about the SGE Dashboard API endpoints, authentication, and usage.

## 🔗 Base URL

**Production**: `https://sge-dashboard-api.onrender.com`  
**Development**: `http://localhost:8000`

## 📋 API Overview

The SGE Dashboard API is built with FastAPI and provides RESTful endpoints for managing grants, tasks, users, and other resources.

### API Version
All endpoints are prefixed with `/api/v1/`

### Content Type
All requests and responses use `application/json`

## 🔐 Authentication

### JWT Authentication
The API uses JWT (JSON Web Tokens) for authentication.

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "admin"
  }
}
```

#### Using the Token
Include the token in the Authorization header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📊 Health Check

### Get System Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "2025-07-18T03:48:19.040Z",
  "environment": "production",
  "version": "1.0.0"
}
```

## 🎯 Grants API

### List Grants
```http
GET /api/v1/grants/
```

**Query Parameters:**
- `skip` (integer): Number of records to skip (default: 0)
- `limit` (integer): Number of records to return (default: 10)
- `search` (string): Search term for title or description
- `status` (string): Filter by status (open, closed, pending)
- `category` (string): Filter by category

**Response:**
```json
{
  "items": [
    {
      "id": "123",
      "title": "Innovation Grant 2025",
      "description": "Funding for innovative projects",
      "amount": 50000,
      "deadline": "2025-12-31T23:59:59Z",
      "status": "open",
      "category": "innovation",
      "created_at": "2025-07-18T03:48:19.040Z",
      "updated_at": "2025-07-18T03:48:19.040Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Get Grant by ID
```http
GET /api/v1/grants/{grant_id}/
```

### Create Grant
```http
POST /api/v1/grants/
Content-Type: application/json

{
  "title": "New Grant Opportunity",
  "description": "Description of the grant",
  "amount": 25000,
  "deadline": "2025-12-31T23:59:59Z",
  "status": "open",
  "category": "research"
}
```

### Update Grant
```http
PUT /api/v1/grants/{grant_id}/
Content-Type: application/json

{
  "title": "Updated Grant Title",
  "status": "closed"
}
```

### Delete Grant
```http
DELETE /api/v1/grants/{grant_id}/
```

## 📝 Tasks API

### List Tasks
```http
GET /api/v1/tasks/
```

**Query Parameters:**
- `skip` (integer): Number of records to skip
- `limit` (integer): Number of records to return
- `status` (string): Filter by status
- `assigned_to` (string): Filter by assigned user

**Response:**
```json
{
  "items": [
    {
      "id": "456",
      "title": "Review Grant Application",
      "description": "Review and evaluate grant application",
      "status": "in_progress",
      "priority": "high",
      "assigned_to": "user123",
      "due_date": "2025-07-25T23:59:59Z",
      "created_at": "2025-07-18T03:48:19.040Z",
      "updated_at": "2025-07-18T03:48:19.040Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Get Task by ID
```http
GET /api/v1/tasks/{task_id}/
```

### Create Task
```http
POST /api/v1/tasks/
Content-Type: application/json

{
  "title": "New Task",
  "description": "Task description",
  "status": "todo",
  "priority": "medium",
  "assigned_to": "user123",
  "due_date": "2025-07-25T23:59:59Z"
}
```

### Update Task
```http
PUT /api/v1/tasks/{task_id}/
Content-Type: application/json

{
  "status": "completed",
  "priority": "high"
}
```

### Delete Task
```http
DELETE /api/v1/tasks/{task_id}/
```

## 👥 Users API

### List Users
```http
GET /api/v1/users/
```

**Response:**
```json
{
  "items": [
    {
      "id": "user123",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "admin",
      "created_at": "2025-07-18T03:48:19.040Z",
      "updated_at": "2025-07-18T03:48:19.040Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Get User by ID
```http
GET /api/v1/users/{user_id}/
```

### Create User
```http
POST /api/v1/users/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "full_name": "Jane Smith",
  "password": "securepassword123",
  "role": "user"
}
```

### Update User
```http
PUT /api/v1/users/{user_id}/
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "role": "admin"
}
```

### Delete User
```http
DELETE /api/v1/users/{user_id}/
```

## 🏷️ Tags API

### List Tags
```http
GET /api/v1/tags/
```

**Response:**
```json
{
  "items": [
    {
      "id": "tag123",
      "name": "innovation",
      "color": "#3B82F6",
      "created_at": "2025-07-18T03:48:19.040Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Create Tag
```http
POST /api/v1/tags/
Content-Type: application/json

{
  "name": "research",
  "color": "#10B981"
}
```

## 💬 Comments API

### List Comments for Task
```http
GET /api/v1/tasks/{task_id}/comments/
```

### Create Comment
```http
POST /api/v1/tasks/{task_id}/comments/
Content-Type: application/json

{
  "content": "This is a comment on the task",
  "parent_id": null
}
```

## 📈 Projects API

### List Projects
```http
GET /api/v1/projects/
```

### Get Project by ID
```http
GET /api/v1/projects/{project_id}/
```

### Create Project
```http
POST /api/v1/projects/
Content-Type: application/json

{
  "title": "New Project",
  "description": "Project description",
  "start_date": "2025-07-18T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z"
}
```

## 🔍 Search API

### Search Grants
```http
GET /api/v1/search/grants?q=innovation
```

### Search Tasks
```http
GET /api/v1/search/tasks?q=review
```

## 📊 Analytics API

### Get Dashboard Stats
```http
GET /api/v1/analytics/dashboard
```

**Response:**
```json
{
  "total_grants": 25,
  "open_grants": 15,
  "total_tasks": 50,
  "completed_tasks": 30,
  "total_users": 10,
  "total_projects": 5
}
```

## ⚠️ Error Handling

### Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-07-18T03:48:19.040Z"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## 🔄 Rate Limiting

The API implements rate limiting to prevent abuse:
- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 📚 Interactive Documentation

### Swagger UI
Visit `https://sge-dashboard-api.onrender.com/api/docs` for interactive API documentation.

### ReDoc
Visit `https://sge-dashboard-api.onrender.com/redoc` for alternative documentation format.

## 🧪 Testing

### Test Endpoints
```http
GET /api/v1/test/health
GET /api/v1/test/database
GET /api/v1/test/email
```

## 🔗 SDKs and Libraries

### JavaScript/TypeScript
```javascript
// Using fetch
const response = await fetch('https://sge-dashboard-api.onrender.com/api/v1/grants/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Using axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://sge-dashboard-api.onrender.com/api/v1',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Python
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://sge-dashboard-api.onrender.com/api/v1/grants/',
    headers=headers
)
```

## 📞 Support

For API support:
1. Check the interactive documentation
2. Review error messages and status codes
3. Test with Postman or similar tools
4. Create an issue in the repository

## 🔗 Quick Links

- **Live API**: https://sge-dashboard-api.onrender.com
- **Health Check**: https://sge-dashboard-api.onrender.com/health
- **Interactive Docs**: https://sge-dashboard-api.onrender.com/api/docs
- **GitHub Repository**: https://github.com/A1anMc/SGEDashboardJuly 