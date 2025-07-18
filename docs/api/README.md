# API Documentation

This document describes the SGE Dashboard API endpoints and their usage.

## 🚀 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://sge-dashboard-api.onrender.com`

## 📚 API Documentation

- **Interactive Docs**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc` (Alternative documentation)

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Authentication Flow

1. **Login**: POST `/api/v1/auth/login`
2. **Use Token**: Include in Authorization header: `Bearer <token>`

### Example Request
```bash
curl -H "Authorization: Bearer <your-jwt-token>" \
     https://sge-dashboard-api.onrender.com/api/v1/grants
```

## 📋 API Endpoints

### Health Check

#### GET `/health`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-15T06:13:45.716287",
  "environment": "production",
  "version": "1.0.0"
}
```

### Authentication

#### POST `/api/v1/auth/login`
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

### Grants

#### GET `/api/v1/grants`
Get all grants with optional filtering.

**Query Parameters:**
- `page`: Page number (default: 1)
- `size`: Items per page (default: 20)
- `status`: Filter by status
- `tag`: Filter by tag
- `search`: Search in title and description

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Media Investment Grant",
      "description": "Grant for media projects",
      "amount": 50000,
      "status": "active",
      "deadline": "2025-12-31",
      "tags": ["media", "investment"],
      "created_at": "2025-07-15T06:13:45.716287"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### POST `/api/v1/grants`
Create a new grant.

**Request Body:**
```json
{
  "title": "New Grant",
  "description": "Grant description",
  "amount": 25000,
  "deadline": "2025-12-31",
  "tags": ["media", "investment"]
}
```

#### GET `/api/v1/grants/{grant_id}`
Get a specific grant by ID.

#### PUT `/api/v1/grants/{grant_id}`
Update a grant.

#### DELETE `/api/v1/grants/{grant_id}`
Delete a grant.

### Tasks

#### GET `/api/v1/tasks`
Get all tasks.

**Query Parameters:**
- `page`: Page number
- `size`: Items per page
- `status`: Filter by status
- `priority`: Filter by priority
- `assigned_to`: Filter by assigned user

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Review Grant Application",
      "description": "Review and evaluate grant application",
      "status": "in_progress",
      "priority": "high",
      "assigned_to": "user@example.com",
      "due_date": "2025-07-20",
      "created_at": "2025-07-15T06:13:45.716287"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### POST `/api/v1/tasks`
Create a new task.

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "priority": "medium",
  "due_date": "2025-07-20",
  "assigned_to": "user@example.com"
}
```

#### GET `/api/v1/tasks/{task_id}`
Get a specific task by ID.

#### PUT `/api/v1/tasks/{task_id}`
Update a task.

#### DELETE `/api/v1/tasks/{task_id}`
Delete a task.

### Comments

#### GET `/api/v1/tasks/{task_id}/comments`
Get comments for a task.

#### POST `/api/v1/tasks/{task_id}/comments`
Add a comment to a task.

**Request Body:**
```json
{
  "content": "This is a comment"
}
```

### Tags

#### GET `/api/v1/tags`
Get all tags.

**Response:**
```json
[
  {
    "id": 1,
    "name": "media",
    "color": "#3B82F6",
    "parent_id": null
  },
  {
    "id": 2,
    "name": "investment",
    "color": "#10B981",
    "parent_id": null
  }
]
```

#### POST `/api/v1/tags`
Create a new tag.

**Request Body:**
```json
{
  "name": "new-tag",
  "color": "#EF4444",
  "parent_id": null
}
```

### Users

#### GET `/api/v1/users/me`
Get current user profile.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-07-15T06:13:45.716287"
}
```

#### PUT `/api/v1/users/me`
Update current user profile.

**Request Body:**
```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com"
}
```

## 🔄 Pagination

Most list endpoints support pagination with the following parameters:

- `page`: Page number (1-based)
- `size`: Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

## 🔍 Filtering

Many endpoints support filtering with query parameters:

- `search`: Text search across multiple fields
- `status`: Filter by status
- `created_at`: Filter by creation date
- `updated_at`: Filter by update date

**Example:**
```
GET /api/v1/grants?search=media&status=active&page=1&size=10
```

## 📊 Error Handling

### Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-07-15T06:13:45.716287"
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

### Validation Errors
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 🔒 Rate Limiting

The API implements rate limiting to prevent abuse:

- **Anonymous**: 100 requests per hour
- **Authenticated**: 1000 requests per hour
- **Premium**: 5000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 📝 Examples

### Using cURL

```bash
# Get all grants
curl -H "Authorization: Bearer <token>" \
     https://sge-dashboard-api.onrender.com/api/v1/grants

# Create a new grant
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"title":"New Grant","description":"Description","amount":25000}' \
     https://sge-dashboard-api.onrender.com/api/v1/grants

# Update a grant
curl -X PUT \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"title":"Updated Grant"}' \
     https://sge-dashboard-api.onrender.com/api/v1/grants/1
```

### Using JavaScript

```javascript
// Get grants
const response = await fetch('https://sge-dashboard-api.onrender.com/api/v1/grants', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const grants = await response.json();

// Create grant
const newGrant = await fetch('https://sge-dashboard-api.onrender.com/api/v1/grants', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'New Grant',
    description: 'Description',
    amount: 25000
  })
});
```

## 🔗 SDKs and Libraries

### Python
```python
import requests

# Get grants
response = requests.get(
    'https://sge-dashboard-api.onrender.com/api/v1/grants',
    headers={'Authorization': f'Bearer {token}'}
)
grants = response.json()
```

### JavaScript/TypeScript
```typescript
// Using axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://sge-dashboard-api.onrender.com',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const grants = await api.get('/api/v1/grants');
```

## 📞 Support

For API support:
- Check the interactive documentation at `/docs`
- Review error messages and status codes
- Contact support team for assistance
- Create an issue in the repository 