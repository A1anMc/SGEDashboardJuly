# Render Deployment Guide

## Prerequisites
- A Render account
- Your code pushed to a Git repository
- Node.js 18+ and Python 3.9+ installed locally for testing

## Project Structure
```
.
├── backend/           # FastAPI backend
├── frontend/         # Next.js frontend
├── render.yaml       # Render configuration
├── .env.production   # Production environment template
└── scripts/         # Deployment verification scripts
```

## Step 1: Local Preparation

1. Test the production configuration locally:
```bash
# Backend
cd backend
pip install -r requirements.txt
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Frontend
cd frontend
npm install
BACKEND_URL=http://localhost:8000 npm run build
npm start
```

2. Verify health endpoints:
```bash
curl http://localhost:8000/health        # Backend health
curl http://localhost:3000/api/health    # Frontend health
```

## Step 2: Render Setup

1. Create a new PostgreSQL database:
   - Go to Render Dashboard → New → PostgreSQL
   - Name: sge-dashboard-db
   - Plan: Starter
   - Copy the internal connection string

2. Create backend service:
   - New → Web Service
   - Connect your repository
   - Name: sge-dashboard-api
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT`
   - Add environment variables from `.env.production`

3. Create frontend service:
   - New → Web Service
   - Name: sge-dashboard-web
   - Environment: Node
   - Build Command: `cd frontend && npm install && npm run build`
   - Start Command: `cd frontend && npm start`
   - Add environment variables:
     - `BACKEND_URL`: URL of your backend service
     - `NODE_ENV`: production

## Step 3: Environment Variables

Required variables for backend:
- `DATABASE_URL`: From Render PostgreSQL
- `SECRET_KEY`: Generate secure random string
- `ENV`: production
- `FRONTEND_URL`: Your frontend service URL
- `CORS_ORIGINS`: Frontend URL, comma-separated if multiple

Required variables for frontend:
- `BACKEND_URL`: Your backend service URL
- `NODE_ENV`: production

## Step 4: Deployment Order

1. Deploy database first
2. Deploy backend service
3. Wait for backend health check to pass
4. Deploy frontend service
5. Verify full system health

## Step 5: Verification

1. Check backend health:
```bash
curl https://sge-dashboard-api.onrender.com/health
```

2. Check frontend health:
```bash
curl https://sge-dashboard-web.onrender.com/api/health
```

3. Run the verification script:
```bash
./scripts/verify-deployment.sh
```

## Troubleshooting

1. Database Connection Issues:
   - Verify DATABASE_URL is correct
   - Check if migrations ran successfully
   - Verify SSL requirements

2. CORS Issues:
   - Check CORS_ORIGINS includes frontend URL
   - Verify frontend uses correct BACKEND_URL

3. Build Failures:
   - Check build logs for missing dependencies
   - Verify Node.js and Python versions

## Monitoring

Basic monitoring is set up through:
- Health check endpoints
- Render's built-in logging
- Database metrics in Render dashboard

## Rollback Plan

If deployment fails:
1. Revert to previous Git commit
2. Redeploy services
3. If database issues, use `alembic downgrade` command

## Security Notes

1. Never commit `.env` files
2. Use Render's environment variable encryption
3. Enable automatic HTTPS redirects
4. Keep dependencies updated 