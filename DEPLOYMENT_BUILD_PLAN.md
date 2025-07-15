# Full-Stack Deployment Build Plan & Process

## 🎯 Overview
This document provides a complete deployment strategy for full-stack applications (Frontend + Backend + Database) with step-by-step processes, checklists, and troubleshooting guides.

## 📋 Pre-Deployment Checklist

### 1. Code Quality & Testing
- [ ] All tests pass locally (`npm test`, `pytest`, etc.)
- [ ] Linting passes (`npm run lint`, `ruff check`, etc.)
- [ ] Type checking passes (`npm run type-check`, `mypy`, etc.)
- [ ] Security scans completed (`npm audit`, `safety check`, etc.)
- [ ] No sensitive data in code (API keys, passwords, etc.)
- [ ] Environment variables properly configured
- [ ] Database migrations tested locally
- [ ] Build process works locally

### 2. Configuration Files
- [ ] `package.json` has correct scripts and dependencies
- [ ] `requirements.txt` (Python) or `Pipfile` is up to date
- [ ] `next.config.js` (Next.js) or equivalent is configured
- [ ] Database schema is version controlled
- [ ] Environment variables documented
- [ ] CORS settings configured for production
- [ ] Health check endpoints implemented

### 3. Infrastructure Setup
- [ ] Cloud platform account created (Render, Vercel, Railway, etc.)
- [ ] Database service provisioned (PostgreSQL, MongoDB, etc.)
- [ ] Environment variables set in cloud platform
- [ ] Domain/URLs planned and configured
- [ ] SSL certificates configured
- [ ] Monitoring/logging setup planned

## 🚀 Deployment Process

### Phase 1: Backend Deployment

#### Step 1: Backend Service Setup
```yaml
# render.yaml or equivalent
services:
  - type: web
    name: your-app-backend
    env: python
    buildCommand: |
      pip install -r requirements.txt
    startCommand: |
      gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
    envVars:
      - key: DATABASE_URL
        sync: false  # Set manually
      - key: SECRET_KEY
        generateValue: true
      - key: ENVIRONMENT
        value: production
    healthCheckPath: /health
    autoDeploy: true
```

#### Step 2: Backend Health Check Implementation
```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}
```

#### Step 3: Database Setup
- [ ] Create database service in cloud platform
- [ ] Set `DATABASE_URL` environment variable
- [ ] Run migrations: `alembic upgrade head`
- [ ] Seed database if needed
- [ ] Test database connection

#### Step 4: Backend Deployment
- [ ] Push code to GitHub
- [ ] Monitor build logs
- [ ] Verify health check passes
- [ ] Test API endpoints
- [ ] Check logs for errors

### Phase 2: Frontend Deployment

#### Step 1: Frontend Service Setup
```yaml
# render.yaml
services:
  - type: web
    name: your-app-frontend
    env: node
    buildCommand: |
      cd frontend
      npm ci --only=production
      npm run build
    startCommand: |
      cd frontend
      PORT=$PORT node .next/standalone/server.js
    envVars:
      - key: NEXT_PUBLIC_API_URL
        value: "https://your-app-backend.onrender.com"
      - key: NODE_ENV
        value: production
    healthCheckPath: /
    autoDeploy: true
```

#### Step 2: Next.js Configuration
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  compress: true,
  env: {
    BACKEND_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  headers: async () => [
    {
      source: '/:path*',
      headers: [
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
      ],
    },
  ],
}

module.exports = nextConfig
```

#### Step 3: Frontend Health Check
```typescript
// pages/api/health.ts or app/api/health/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ status: 'healthy', service: 'frontend' })
}
```

#### Step 4: Frontend Deployment
- [ ] Push code to GitHub
- [ ] Monitor build logs
- [ ] Verify frontend loads
- [ ] Test API integration
- [ ] Check for console errors

### Phase 3: Integration & Testing

#### Step 1: CORS Configuration
```python
# Backend CORS setup
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app-frontend.onrender.com",
        "http://localhost:3000"  # for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Step 2: Environment Variables
```bash
# Backend Environment Variables
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
ENVIRONMENT=production
FRONTEND_URL=https://your-app-frontend.onrender.com

# Frontend Environment Variables
NEXT_PUBLIC_API_URL=https://your-app-backend.onrender.com
NODE_ENV=production
```

#### Step 3: Integration Testing
- [ ] Test frontend → backend communication
- [ ] Verify authentication flows
- [ ] Test database operations
- [ ] Check error handling
- [ ] Verify file uploads (if applicable)
- [ ] Test real-time features (if applicable)

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Build Failures
**Symptoms:** Build logs show errors, deployment fails
**Solutions:**
- Check dependency versions in `package.json`/`requirements.txt`
- Verify build commands work locally
- Check for missing environment variables
- Ensure all dependencies are in production dependencies

#### 2. Health Check Failures
**Symptoms:** Service shows as unhealthy, 502 errors
**Solutions:**
- Verify health check path exists and returns 200
- Check if service is binding to correct port
- Review start command syntax
- Check logs for startup errors

#### 3. Database Connection Issues
**Symptoms:** 500 errors, database connection errors
**Solutions:**
- Verify `DATABASE_URL` is correct
- Check database service is running
- Run migrations manually if needed
- Test connection locally with production URL

#### 4. CORS Errors
**Symptoms:** Frontend can't connect to backend, CORS errors in console
**Solutions:**
- Update CORS origins in backend
- Check frontend API URL configuration
- Verify HTTPS/HTTP protocol matching

#### 5. Port Binding Issues
**Symptoms:** Service won't start, port already in use
**Solutions:**
- Use `$PORT` environment variable
- Check start command uses correct port
- Verify no hardcoded ports in code

### Debugging Commands

#### Backend Debugging
```bash
# Test backend locally with production settings
DATABASE_URL=your-prod-db-url uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test database connection
python -c "from app.db.session import engine; print(engine.execute('SELECT 1').scalar())"

# Check health endpoint
curl http://localhost:8000/health
```

#### Frontend Debugging
```bash
# Test build locally
cd frontend && npm run build

# Test standalone server
cd frontend && PORT=3000 node .next/standalone/server.js

# Check environment variables
echo $NEXT_PUBLIC_API_URL
```

## 📊 Monitoring & Maintenance

### Health Monitoring
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure error tracking (Sentry, LogRocket)
- [ ] Set up performance monitoring
- [ ] Configure log aggregation

### Regular Maintenance
- [ ] Update dependencies monthly
- [ ] Review security advisories
- [ ] Monitor resource usage
- [ ] Backup database regularly
- [ ] Test disaster recovery procedures

## 🎯 Success Criteria

### Deployment Success Checklist
- [ ] Backend responds to health checks
- [ ] Frontend loads without errors
- [ ] API endpoints return correct responses
- [ ] Database operations work
- [ ] Authentication flows work
- [ ] No console errors in browser
- [ ] SSL certificates valid
- [ ] Performance acceptable (<3s load time)

### Post-Deployment Testing
- [ ] Test all major user flows
- [ ] Verify data persistence
- [ ] Test error handling
- [ ] Check mobile responsiveness
- [ ] Verify accessibility features
- [ ] Test with different browsers

## 📝 Template Files

### render.yaml Template
```yaml
services:
  # Backend
  - type: web
    name: your-app-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /health
    autoDeploy: true

  # Frontend
  - type: web
    name: your-app-frontend
    env: node
    buildCommand: |
      cd frontend
      npm ci --only=production
      npm run build
    startCommand: |
      cd frontend
      PORT=$PORT node .next/standalone/server.js
    envVars:
      - key: NEXT_PUBLIC_API_URL
        value: "https://your-app-backend.onrender.com"
    healthCheckPath: /
    autoDeploy: true
```

### package.json Scripts Template
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "PORT=$PORT node .next/standalone/server.js",
    "lint": "next lint",
    "test": "jest",
    "type-check": "tsc --noEmit"
  }
}
```

## 🚨 Emergency Procedures

### Rollback Process
1. Identify the problematic deployment
2. Revert to previous working commit
3. Push changes to trigger new deployment
4. Verify rollback success
5. Investigate root cause

### Database Recovery
1. Check database service status
2. Restore from backup if needed
3. Run migrations if necessary
4. Verify data integrity
5. Update application if schema changed

This plan should help you deploy any full-stack application efficiently while avoiding common pitfalls and having clear troubleshooting procedures. 