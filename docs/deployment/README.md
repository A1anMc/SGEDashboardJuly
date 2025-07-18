# Deployment Guide

This guide covers deploying the SGE Dashboard to production environments.

## 🚀 Production Deployment

### Current Deployment

The application is deployed on **Render** with the following services:

- **Backend API**: `https://sge-dashboard-api.onrender.com`
- **Frontend**: `https://sge-dashboard-web-new.onrender.com`

### Render Configuration

#### Backend Service (`sge-dashboard-api`)
```yaml
type: web
env: python
buildCommand: pip install -r requirements.txt
startCommand: gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2
healthCheckPath: /health
```

#### Frontend Service (`sge-dashboard-web-new`)
```yaml
type: web
env: node
buildCommand: |
  npm ci --only=production
  npm run build
  cp -r .next/static .next/standalone/.next/ || true
  cp -r public .next/standalone/ || true
startCommand: cd .next/standalone && PORT=$PORT node server.js
healthCheckPath: /
```

## 🔧 Environment Variables

### Backend Environment Variables
```env
RENDER=true
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
FRONTEND_URL=https://sge-dashboard-web-new.onrender.com
CORS_ORIGINS=["https://sge-dashboard-web-new.onrender.com"]
```

### Frontend Environment Variables
```env
NEXT_PUBLIC_API_URL=https://sge-dashboard-api.onrender.com
NODE_ENV=production
NEXT_PUBLIC_ENV=production
PORT=3000
```

## 📊 Health Checks

### Backend Health Check
- **Endpoint**: `/health`
- **Expected Response**: `{"status":"healthy","timestamp":"...","environment":"production","version":"1.0.0"}`

### Frontend Health Check
- **Endpoint**: `/`
- **Expected Response**: HTML page with dashboard

## 🔄 Deployment Process

### 1. Backend Deployment
1. Push changes to `main` branch
2. Render automatically builds and deploys
3. Health check confirms service is running
4. API endpoints are available

### 2. Frontend Deployment
1. Push changes to `main` branch
2. Render builds Next.js application
3. Static assets are copied to standalone directory
4. Service starts with standalone server
5. Health check confirms service is running

## 🐛 Troubleshooting

### Common Issues

#### 502 Bad Gateway
- Check Render logs for build errors
- Verify environment variables are set
- Confirm health check endpoints are working

#### Build Failures
- Check for missing dependencies
- Verify Node.js/Python versions
- Review build command syntax

#### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check database is accessible from Render
- Confirm SSL settings

### Monitoring

#### Render Dashboard
- Monitor service health status
- Check resource usage (CPU, Memory)
- Review deployment logs

#### Application Logs
- Backend logs available in Render dashboard
- Frontend errors visible in browser console
- API errors logged in backend

## 🔒 Security

### CORS Configuration
```python
CORS_ORIGINS = [
    "https://sge-dashboard-web-new.onrender.com",
    "https://sge-dashboard-api.onrender.com"
]
```

### Security Headers
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`

## 📈 Scaling

### Current Configuration
- **Min Instances**: 1
- **Max Instances**: 2
- **Target Memory**: 70%
- **Target CPU**: 70%

### Auto-scaling
- Services automatically scale based on load
- New instances are created when needed
- Idle instances are scaled down to save costs

## 🔄 Rollback Process

### Emergency Rollback
1. Access Render dashboard
2. Navigate to service settings
3. Click "Rollback" to previous deployment
4. Confirm rollback action

### Manual Rollback
1. Revert to previous git commit
2. Push changes to trigger new deployment
3. Monitor deployment status

## 📞 Support

For deployment issues:
1. Check Render documentation
2. Review application logs
3. Contact support team
4. Create issue in repository 