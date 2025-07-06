# 🚀 Render Deployment Guide

## 📋 Pre-Deployment Checklist

Run this first:
```bash
bash scripts/verify-deploy.sh
```

## 🗂️ Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"PostgreSQL"**
3. **Name**: `sge-dashboard-db`
4. **Database**: `sge_dashboard`
5. **User**: `sge_dashboard_user`
6. **Plan**: Starter (free)
7. Click **"Create Database"**
8. **📋 SAVE THE DATABASE URL** - you'll need it!

## 🔧 Step 2: Deploy Backend Service

1. Click **"New"** → **"Web Service"**
2. **Connect Repository**: Choose your GitHub repo
3. **Service Name**: `sge-dashboard-api`
4. **Root Directory**: `/` (leave empty)
5. **Environment**: `Python`
6. **Build Command**: 
   ```
   pip install -r requirements.txt
   ```
7. **Start Command**: 
   ```
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT --timeout 120
   ```
8. **Health Check Path**: `/health`

### Environment Variables for Backend:
```
DATABASE_URL = <paste-your-database-url-here>
SECRET_KEY = <generate-32-character-secure-key>
FRONTEND_URL = https://sge-dashboard-web.onrender.com
CORS_ORIGINS = https://sge-dashboard-web.onrender.com,https://*.onrender.com
ENVIRONMENT = production
DEBUG = false
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10
```

9. Click **"Create Web Service"**
10. **Wait for deployment** (5-10 minutes)

## 🧪 Step 3: Test Backend Health

Once deployed, run:
```bash
./scripts/check-backend-health.sh
```

If it fails, check logs at: `https://dashboard.render.com/web/sge-dashboard-api`

## 🎨 Step 4: Deploy Frontend Service

**⚠️ ONLY after backend health check passes!**

1. Click **"New"** → **"Web Service"**
2. **Connect Repository**: Same GitHub repo
3. **Service Name**: `sge-dashboard-web`
4. **Root Directory**: `frontend`
5. **Environment**: `Node`
6. **Build Command**: 
   ```
   npm install && npm run build
   ```
7. **Start Command**: 
   ```
   npm start
   ```

### Environment Variables for Frontend:
```
NODE_ENV = production
NEXT_PUBLIC_API_URL = https://sge-dashboard-api.onrender.com
```

8. Click **"Create Web Service"**
9. **Wait for deployment** (5-10 minutes)

## ✅ Step 5: Final Verification

1. **Backend Health**: https://sge-dashboard-api.onrender.com/health
2. **Frontend**: https://sge-dashboard-web.onrender.com
3. **Full Integration**: Test login/signup on frontend

## 🚨 Troubleshooting

### Backend Issues:
- **500 Error**: Check database connection string
- **Import Error**: Verify all dependencies in requirements.txt
- **Timeout**: Increase timeout in start command

### Frontend Issues:
- **Build Failed**: Check Node.js version (should be 18+)
- **API Errors**: Verify CORS settings in backend
- **404 on Routes**: Check Next.js configuration

### Database Issues:
- **Connection Failed**: Verify DATABASE_URL format
- **Migration Error**: Check alembic configuration

## 🔄 Rollback Plan

If deployment fails:
1. **Disable Auto-Deploy** in Render dashboard
2. **Revert to Previous Deploy** using Render's rollback feature
3. **Check Logs** for specific error messages
4. **Fix Issues Locally** and redeploy

## 📞 Support

- **Render Logs**: Dashboard → Service → Logs
- **Health Checks**: Use provided scripts
- **Database**: Check connection from Render dashboard

---

🎉 **Success!** Your full-stack app should now be live on Render! 