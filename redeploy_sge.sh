#!/bin/bash

# ====== CONFIG ======
FRONTEND_SERVICE_ID="sge-dashboard-web"   # Your frontend service name
BACKEND_SERVICE_ID="sge-dashboard-api"    # Your backend service name
BACKEND_URL="https://sge-dashboard-api.onrender.com/health"
FRONTEND_URL="https://sge-dashboard-web.onrender.com"

echo "🚀 Starting One-Shot Redeploy for SGE Dashboard..."

# ====== STEP 1: FRONTEND REDEPLOY ======
echo "🔄 Redeploying Frontend..."
render deploy $FRONTEND_SERVICE_ID --wait

echo "✅ Frontend redeployed. Waiting 15s for it to come online..."
sleep 15

echo "🌐 Checking Frontend Health..."
curl -I $FRONTEND_URL

# ====== STEP 2: BACKEND DB SSL FIX ======
echo "🔧 Updating Backend DB SSL Mode..."
render env:set $BACKEND_SERVICE_ID DATABASE_URL "$(render env:get $BACKEND_SERVICE_ID DATABASE_URL)?sslmode=require"

echo "✅ DATABASE_URL updated with sslmode=require"

# ====== STEP 3: BACKEND ENV + CORS CONFIG ======
echo "🔧 Setting Backend Production ENV + Allowed Origins..."
render env:set $BACKEND_SERVICE_ID ENVIRONMENT "production"
render env:set $BACKEND_SERVICE_ID CORS_ORIGINS '["https://sge-dashboard-web.onrender.com", "https://sge-dashboard-api.onrender.com", "https://*.onrender.com"]'

echo "✅ Backend ENV + CORS updated"

# ====== STEP 4: BACKEND REDEPLOY ======
echo "🔄 Redeploying Backend..."
render deploy $BACKEND_SERVICE_ID --wait

echo "✅ Backend redeployed. Waiting 15s for it to come online..."
sleep 15

# ====== STEP 5: HEALTH CHECKS ======
echo "🌐 Checking Backend Health..."
curl -I $BACKEND_URL

echo "✅ One-Shot Redeploy Completed!"
echo "🎯 Frontend: $FRONTEND_URL"
echo "🎯 Backend: $BACKEND_URL" 