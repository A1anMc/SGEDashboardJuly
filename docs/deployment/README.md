# Deployment Guide

This guide covers deploying the SGE Dashboard to production environments.

## 🚀 Production Deployment

### Current Deployment Status

The application is deployed on **Render** with the following services:

- **Backend API**: `https://sge-dashboard-api.onrender.com` ✅ **LIVE**
- **Frontend**: `https://sge-dashboard-web-new.onrender.com` 🚧 **READY FOR DEPLOYMENT**

### System Status

#### Backend Service (`sge-dashboard-api`) ✅
- **Status**: Healthy and running
- **Health Check**: `https://sge-dashboard-api.onrender.com/health`
- **API Documentation**: `https://sge-dashboard-api.onrender.com/api/docs`
- **Database**: PostgreSQL connected and operational
- **Features**: All API endpoints restored and functional

#### Frontend Service (`sge-dashboard-web-new`) 🚧
- **Status**: Ready for deployment
- **Local Testing**: `http://localhost:3000` ✅ Working
- **API Integration**: Direct connection to backend ✅
- **Build**: Next.js 15 with standalone configuration ✅

## 🔧 Render Configuration

### Backend Service Configuration
```yaml
type: web
env: python
buildCommand: pip install -r requirements.txt
startCommand: gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
healthCheckPath: /health
```

### Frontend Service Configuration
```yaml
type: web
env: node
buildCommand: |
  cd frontend
  npm ci --only=production
  npm run build
  cp -r .next/static .next/standalone/.next/ || true
  cp -r public .next/standalone/ || true
startCommand: cd frontend/.next/standalone && PORT=$PORT node server.js
healthCheckPath: /api/health
rootDirectory: frontend
```

## 🔧 Environment Variables

### Backend Environment Variables
```env
RENDER=true
ENV=production
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
NEXT_PUBLIC_APP_NAME=SGE Dashboard
NODE_ENV=production
NEXT_PUBLIC_ENV=production
PORT=3000
```

## 📊 Health Checks

### Backend Health Check ✅
- **Endpoint**: `https://sge-dashboard-api.onrender.com/health`
- **Expected Response**: 
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "2025-07-18T03:48:19.040Z",
  "environment": "production",
  "version": "1.0.0"
}
```

### Frontend Health Check 🚧
- **Endpoint**: `/api/health` (after deployment)
- **Expected Response**: 
```json
{
  "status": "healthy",
  "service": "frontend",
  "timestamp": "2025-07-18T03:48:19.040Z"
}
```

## 🔄 Deployment Process

### 1. Backend Deployment ✅ COMPLETED
1. ✅ Code pushed to `main` branch
2. ✅ Render automatically built and deployed
3. ✅ Health check confirms service is running
4. ✅ All API endpoints are available and functional
5. ✅ Database connected and migrations applied

### 2. Frontend Deployment 🚧 READY
1. ✅ Code prepared and tested locally
2. ✅ API integration verified
3. ✅ Build configuration optimized
4. 🚧 **NEXT**: Deploy to Render
5. 🚧 **NEXT**: Verify health checks
6. 🚧 **NEXT**: Test end-to-end functionality

## 🚀 Frontend Deployment Steps

### Step 1: Create Render Service
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect to GitHub repository: `A1anMc/SGEDashboardJuly`
4. Configure service settings

### Step 2: Configure Build Settings
- **Name**: `sge-dashboard-web-new`
- **Environment**: Node
- **Build Command**: 
```bash
cd frontend && npm ci --only=production && npm run build
```
- **Start Command**: 
```bash
cd frontend/.next/standalone && PORT=$PORT node server.js
```
- **Root Directory**: `frontend`

### Step 3: Set Environment Variables
```
NEXT_PUBLIC_API_URL=https://sge-dashboard-api.onrender.com
NEXT_PUBLIC_APP_NAME=SGE Dashboard
NODE_ENV=production
```

### Step 4: Configure Health Check
- **Health Check Path**: `/api/health`
- **Timeout**: 30 seconds

## 🐛 Troubleshooting

### Common Issues

#### 502 Bad Gateway
- Check Render logs for build errors
- Verify environment variables are set
- Confirm health check endpoints are working
- Check for missing dependencies

#### Build Failures
- Verify Node.js version (18+)
- Check for missing dependencies in package.json
- Review build command syntax
- Check for TypeScript compilation errors

#### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check database is accessible from Render
- Confirm SSL settings
- Check connection pool settings

#### API Communication Issues
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS configuration
- Test API endpoints directly
- Review network requests in browser

### Monitoring

#### Render Dashboard
- Monitor service health status
- Check resource usage (CPU, Memory)
- Review deployment logs
- Monitor build times

#### Application Logs
- Backend logs available in Render dashboard
- Frontend errors visible in browser console
- API errors logged in backend
- Health check failures trigger alerts

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
- `Content-Security-Policy: default-src 'self'`

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
3. Test locally first
4. Create issue in repository

## 🔗 Quick Links

- **Backend Health**: https://sge-dashboard-api.onrender.com/health
- **API Documentation**: https://sge-dashboard-api.onrender.com/api/docs
- **Render Dashboard**: https://dashboard.render.com
- **GitHub Repository**: https://github.com/A1anMc/SGEDashboardJuly 