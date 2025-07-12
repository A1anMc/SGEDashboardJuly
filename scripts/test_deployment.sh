#!/bin/bash

echo "🔍 Testing SGE Dashboard Deployment"
echo "=================================="

echo "1. Testing Backend Health..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://sge-dashboard-api.onrender.com/health)
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ Backend Health: OK ($BACKEND_STATUS)"
else
    echo "❌ Backend Health: FAILED ($BACKEND_STATUS)"
fi

echo "2. Testing Backend Root..."
ROOT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://sge-dashboard-api.onrender.com/)
if [ "$ROOT_STATUS" = "200" ]; then
    echo "✅ Backend Root: OK ($ROOT_STATUS)"
else
    echo "❌ Backend Root: FAILED ($ROOT_STATUS)"
fi

echo "3. Testing Frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://sge-dashboard-web.onrender.com/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend: OK ($FRONTEND_STATUS)"
else
    echo "❌ Frontend: FAILED ($FRONTEND_STATUS)"
fi

echo "=================================="
if [ "$BACKEND_STATUS" = "200" ] && [ "$FRONTEND_STATUS" = "200" ]; then
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "Your SGE Dashboard is now running:"
    echo "- Frontend: https://sge-dashboard-web.onrender.com"
    echo "- Backend API: https://sge-dashboard-api.onrender.com"
else
    echo "❌ DEPLOYMENT ISSUES DETECTED"
    echo "Check Render service logs for details"
fi 