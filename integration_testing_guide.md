# Frontend-Backend Integration Testing Guide

## Phase 1: Backend Setup and Validation

### Step 1: Verify Backend Environment
```bash
# Navigate to backend directory
cd backend

# Check if virtual environment exists
ls -la venv/

# If not, create it
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Setup
```bash
# Check database connection
python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('Database connection successful')"

# Run database migrations
alembic upgrade head

# Optional: Seed test data
python -c "from app.db.seed_data import seed_database; seed_database()"
```

### Step 3: Start Backend Server
```bash
# Method 1: Direct Python execution
python app/main.py

# Method 2: Using uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 3: Using the root main.py if it exists
python main.py
```

### Step 4: Test Backend API Endpoints
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API documentation
curl http://localhost:8000/docs
# Open in browser: http://localhost:8000/docs

# Test specific endpoints
curl -X GET http://localhost:8000/api/v1/users
curl -X GET http://localhost:8000/api/v1/grants
curl -X GET http://localhost:8000/api/v1/projects
```

## Phase 2: Frontend Setup and Validation

### Step 5: Verify Frontend Environment
```bash
# Navigate to frontend directory
cd new-frontend

# Check Node.js version (should be 18+ for Next.js)
node --version
npm --version

# Install dependencies
npm install

# Check for TypeScript errors
npx tsc --noEmit
```

### Step 6: Configure Frontend Environment
```bash
# Create environment file
cp .env.example .env.local
# or create new .env.local file

# Add backend URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1" >> .env.local
```

### Step 7: Start Frontend Development Server
```bash
# Start Next.js development server
npm run dev

# Alternative commands to try
npm run start
npm run build && npm run start
```

## Phase 3: Integration Testing

### Step 8: Test Basic Connectivity
Open browser dev tools (F12) and navigate to `http://localhost:3000`

**Check for CORS errors:**
```javascript
// In browser console, test API connectivity
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log('Backend connection successful:', data))
  .catch(error => console.error('Backend connection failed:', error));
```

### Step 9: Test API Integration
```javascript
// Test authenticated endpoints (if applicable)
fetch('http://localhost:8000/api/v1/users', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN_HERE',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log('Users API:', data))
.catch(error => console.error('Users API error:', error));
```

### Step 10: Test Different HTTP Methods
```javascript
// Test POST request
fetch('http://localhost:8000/api/v1/projects', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN_HERE'
  },
  body: JSON.stringify({
    name: 'Test Project',
    description: 'Integration test project'
  })
})
.then(response => response.json())
.then(data => console.log('POST successful:', data))
.catch(error => console.error('POST failed:', error));
```

## Phase 4: Troubleshooting Common Issues

### Issue 1: CORS Errors
**Symptoms:** `Access-Control-Allow-Origin` errors in browser console

**Solution:**
1. Check backend CORS configuration in `app/main.py`
2. Ensure frontend URL is in allowed origins
3. Add credentials support if using authentication

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: API Endpoint Not Found
**Symptoms:** 404 errors when calling API endpoints

**Solution:**
1. Check API route definitions in `backend/app/routers/`
2. Verify URL structure matches frontend expectations
3. Check if API prefix is configured correctly

```bash
# Test actual backend routes
curl -X GET http://localhost:8000/api/v1/users
curl -X GET http://localhost:8000/users
# Try both with and without /api/v1 prefix
```

### Issue 3: Authentication Issues
**Symptoms:** 401/403 errors on protected endpoints

**Solution:**
1. Test authentication endpoint first
2. Verify token format and expiration
3. Check header format

```javascript
// Test authentication
fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'test@example.com',
    password: 'testpassword'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Auth response:', data);
  // Use token for subsequent requests
});
```

### Issue 4: Database Connection Issues
**Symptoms:** 500 errors from backend, database connection errors

**Solution:**
1. Check database service is running
2. Verify connection string
3. Test connection manually

```bash
# Check database status
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # Mac

# Test connection
psql -h localhost -U your_username -d your_database
```

## Phase 5: End-to-End Testing

### Step 11: Test Complete User Flow
1. **Registration/Login:**
   - Test user registration
   - Test login functionality
   - Verify token storage and usage

2. **Data Operations:**
   - Test creating new records
   - Test reading/listing data
   - Test updating records
   - Test deletion

3. **File Operations (if applicable):**
   - Test file upload
   - Test file download
   - Test media display

### Step 12: Performance Testing
```bash
# Test concurrent requests
for i in {1..10}; do
  curl -X GET http://localhost:8000/api/v1/users &
done
wait
```

## Phase 6: Production Readiness

### Step 13: Environment Configuration
```bash
# Backend production settings
export DATABASE_URL="postgresql://user:pass@localhost/prod_db"
export SECRET_KEY="your-secret-key-here"
export CORS_ORIGINS="https://yourdomain.com"

# Frontend production build
npm run build
npm run start
```

### Step 14: Security Checklist
- [ ] Remove debug information from production
- [ ] Verify CORS is restrictive in production
- [ ] Check HTTPS configuration
- [ ] Validate authentication security
- [ ] Test rate limiting
- [ ] Verify input validation

## Automated Testing Scripts

### Backend API Test Script
```bash
#!/bin/bash
# test_backend.sh

echo "Testing backend API..."

# Test health endpoint
if curl -f http://localhost:8000/health; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint failed"
    exit 1
fi

# Test API documentation
if curl -f http://localhost:8000/docs; then
    echo "✅ API docs accessible"
else
    echo "❌ API docs failed"
fi

# Add more endpoint tests here
echo "Backend tests completed"
```

### Frontend Integration Test Script
```bash
#!/bin/bash
# test_frontend.sh

echo "Testing frontend integration..."

# Start frontend (if not already running)
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

# Test frontend accessibility
if curl -f http://localhost:3000; then
    echo "✅ Frontend accessible"
else
    echo "❌ Frontend failed to start"
    kill $FRONTEND_PID
    exit 1
fi

# Clean up
kill $FRONTEND_PID
echo "Frontend tests completed"
```

## Monitoring and Logging

### Backend Logging
```python
# Add to backend/app/main.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log API requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"API Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"API Response: {response.status_code}")
    return response
```

### Frontend Error Handling
```javascript
// Add to frontend for API error handling
const apiClient = {
  async request(url, options = {}) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }
};
```

## Success Criteria

Your integration is successful when:
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] No CORS errors in browser console
- [ ] API endpoints return expected data
- [ ] Authentication flow works completely
- [ ] Database operations succeed
- [ ] File uploads work (if applicable)
- [ ] Error handling works properly
- [ ] Performance is acceptable

## Next Steps

Once integration is working:
1. Set up CI/CD pipeline
2. Add comprehensive testing suite
3. Configure monitoring and alerting
4. Plan deployment strategy
5. Document API for frontend developers

This guide should help you systematically validate and troubleshoot your frontend-backend integration. Work through each phase methodically, and you'll identify and resolve any integration issues.