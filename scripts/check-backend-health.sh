#!/bin/bash

# ---- Config ----
BACKEND_URL=${1:-https://sge-dashboard-api.onrender.com}
HEALTH_PATH="/health"

echo "🔍 Checking health endpoint at: $BACKEND_URL$HEALTH_PATH"

# ---- Execute ----
response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$HEALTH_PATH")

if [ "$response" == "200" ]; then
    echo "✅ Backend is healthy! ($response)"
    exit 0
else
    echo "❌ Backend health check failed. Status code: $response"
    echo "📎 Check logs at: https://dashboard.render.com/web/sge-dashboard-api"
    exit 1
fi 