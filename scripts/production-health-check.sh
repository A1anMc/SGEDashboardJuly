#!/bin/bash

# Production Health Check Script for SGE Dashboard
# This script helps diagnose production deployment issues

echo "🔍 SGE Dashboard Production Health Check"
echo "========================================"

# Configuration
BACKEND_URL="https://sge-dashboard-api.onrender.com"
FRONTEND_URL="https://sge-dashboard-web.onrender.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check HTTP status
check_endpoint() {
    local url=$1
    local service=$2
    local timeout=10
    
    echo -n "Checking $service ($url)... "
    
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url")
    response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time $timeout "$url")
    
    if [ "$status_code" -eq 200 ]; then
        echo -e "${GREEN}✓ Healthy${NC} (${status_code}, ${response_time}s)"
        return 0
    elif [ "$status_code" -eq 503 ]; then
        echo -e "${RED}✗ Service Unavailable${NC} (${status_code})"
        return 1
    elif [ "$status_code" -eq 000 ]; then
        echo -e "${RED}✗ Connection Failed${NC} (timeout)"
        return 1
    else
        echo -e "${YELLOW}⚠ Issue Detected${NC} (${status_code})"
        return 1
    fi
}

# Function to check API endpoints
check_api_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -n "Testing $description... "
    
    response=$(curl -s --max-time 15 "$BACKEND_URL$endpoint" 2>/dev/null)
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$BACKEND_URL$endpoint")
    
    if [ "$status_code" -eq 200 ]; then
        echo -e "${GREEN}✓ Working${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed${NC} (${status_code})"
        return 1
    fi
}

# Main health checks
echo ""
echo "🏥 Core Service Health"
echo "----------------------"

# Check backend health endpoint
backend_healthy=false
if check_endpoint "$BACKEND_URL/health" "Backend Health"; then
    backend_healthy=true
    
    # Get detailed health info
    echo "Backend Health Details:"
    curl -s "$BACKEND_URL/health" | python3 -m json.tool 2>/dev/null || echo "Could not parse health response"
    echo ""
fi

# Check frontend
frontend_healthy=false
if check_endpoint "$FRONTEND_URL" "Frontend"; then
    frontend_healthy=true
fi

echo ""
echo "🔌 API Endpoint Tests"
echo "--------------------"

if [ "$backend_healthy" = true ]; then
    check_api_endpoint "/api/v1/grants?skip=0&limit=5" "Grants API"
    check_api_endpoint "/api/v1/projects?skip=0&limit=5" "Projects API"
    
    # Test API through frontend proxy
    echo -n "Testing Frontend API Proxy... "
    proxy_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$FRONTEND_URL/api/grants?skip=0&limit=5")
    if [ "$proxy_status" -eq 200 ]; then
        echo -e "${GREEN}✓ Working${NC}"
    else
        echo -e "${RED}✗ Failed${NC} (${proxy_status})"
    fi
else
    echo -e "${RED}⚠ Skipping API tests - backend unhealthy${NC}"
fi

echo ""
echo "📊 System Status Summary"
echo "------------------------"

if [ "$backend_healthy" = true ] && [ "$frontend_healthy" = true ]; then
    echo -e "${GREEN}✓ System Status: HEALTHY${NC}"
    echo "Both frontend and backend are responding correctly."
elif [ "$backend_healthy" = false ] && [ "$frontend_healthy" = true ]; then
    echo -e "${RED}✗ System Status: BACKEND DOWN${NC}"
    echo "Frontend is working but backend is unavailable (503 errors)."
    echo ""
    echo "🛠️  Suggested Actions:"
    echo "1. Check Render dashboard for backend service logs"
    echo "2. Verify database connection and environment variables"
    echo "3. Check for database migration failures"
    echo "4. Review worker timeout settings"
elif [ "$backend_healthy" = true ] && [ "$frontend_healthy" = false ]; then
    echo -e "${YELLOW}⚠ System Status: FRONTEND ISSUES${NC}"
    echo "Backend is working but frontend has issues."
elif [ "$backend_healthy" = false ] && [ "$frontend_healthy" = false ]; then
    echo -e "${RED}✗ System Status: SYSTEM DOWN${NC}"
    echo "Both services are experiencing issues."
else
    echo -e "${YELLOW}⚠ System Status: UNKNOWN${NC}"
    echo "Could not determine system health."
fi

echo ""
echo "🔧 Common 503 Error Causes:"
echo "- Database connection failures"
echo "- Worker process timeouts"
echo "- Memory/CPU resource exhaustion"
echo "- Database migration failures"
echo "- Missing environment variables"
echo ""
echo "📋 To resolve 503 errors:"
echo "1. Check Render service logs for specific error messages"
echo "2. Verify DATABASE_URL is correctly set"
echo "3. Ensure database is accessible and not overloaded"
echo "4. Check if alembic migrations are failing"
echo "5. Monitor resource usage (CPU/Memory)"
echo ""
echo "Run this script periodically to monitor deployment health." 