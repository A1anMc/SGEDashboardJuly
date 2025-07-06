#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Deployment Validation Script${NC}"
echo -e "${BLUE}================================${NC}"

# Check if we're validating local or remote
BACKEND_URL=${1:-"https://sge-dashboard-api.onrender.com"}
FRONTEND_URL=${2:-"https://sge-dashboard-web.onrender.com"}

echo -e "\n${YELLOW}🎯 Target URLs:${NC}"
echo -e "Backend:  $BACKEND_URL"
echo -e "Frontend: $FRONTEND_URL"

# Function to check HTTP status
check_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    local timeout=${3:-10}
    
    echo -n "Checking $url... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" 2>/dev/null || echo "000")
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✅ $status${NC}"
        return 0
    else
        echo -e "${RED}❌ $status${NC}"
        return 1
    fi
}

# Function to check JSON response
check_json_endpoint() {
    local url=$1
    local expected_key=$2
    
    echo -n "Checking $url for JSON... "
    
    response=$(curl -s --max-time 10 "$url" 2>/dev/null || echo "{}")
    
    if echo "$response" | jq -e ".$expected_key" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Valid JSON${NC}"
        return 0
    else
        echo -e "${RED}❌ Invalid JSON or missing key '$expected_key'${NC}"
        return 1
    fi
}

# Validation counters
TOTAL_CHECKS=0
PASSED_CHECKS=0

# 1. Backend Health Check
echo -e "\n${YELLOW}🔧 Backend Validation${NC}"
echo -e "${YELLOW}--------------------${NC}"

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if check_endpoint "$BACKEND_URL/health"; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if check_json_endpoint "$BACKEND_URL/health" "status"; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# 2. Backend API Endpoints
echo -e "\n${YELLOW}📡 API Endpoints${NC}"
echo -e "${YELLOW}----------------${NC}"

api_endpoints=(
    "/docs"
    "/openapi.json"
    "/api/v1/auth/me"
)

for endpoint in "${api_endpoints[@]}"; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    # For auth endpoints, 401 is expected without token
    if [[ "$endpoint" == *"/auth/"* ]]; then
        if check_endpoint "$BACKEND_URL$endpoint" "401"; then
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        fi
    else
        if check_endpoint "$BACKEND_URL$endpoint" "200"; then
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        fi
    fi
done

# 3. Frontend Validation
echo -e "\n${YELLOW}🎨 Frontend Validation${NC}"
echo -e "${YELLOW}---------------------${NC}"

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if check_endpoint "$FRONTEND_URL"; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# 4. CORS Check
echo -e "\n${YELLOW}🌐 CORS Validation${NC}"
echo -e "${YELLOW}------------------${NC}"

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
echo -n "Checking CORS headers... "
cors_headers=$(curl -s -I -H "Origin: $FRONTEND_URL" "$BACKEND_URL/health" | grep -i "access-control" || echo "")
if [ -n "$cors_headers" ]; then
    echo -e "${GREEN}✅ CORS headers present${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}❌ CORS headers missing${NC}"
fi

# 5. Database Connection (via health endpoint)
echo -e "\n${YELLOW}🗄️  Database Validation${NC}"
echo -e "${YELLOW}----------------------${NC}"

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if check_endpoint "$BACKEND_URL/health/detailed"; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    echo -n "Checking database connection... "
    db_status=$(curl -s "$BACKEND_URL/health/detailed" | jq -r '.database.status' 2>/dev/null || echo "unknown")
    if [ "$db_status" = "connected" ]; then
        echo -e "${GREEN}✅ Database connected${NC}"
    else
        echo -e "${RED}❌ Database connection issue${NC}"
    fi
fi

# 6. Environment Variables Check (via health endpoint)
echo -e "\n${YELLOW}🔧 Environment Check${NC}"
echo -e "${YELLOW}-------------------${NC}"

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
echo -n "Checking environment configuration... "
env_status=$(curl -s "$BACKEND_URL/health/detailed" | jq -r '.environment' 2>/dev/null || echo "unknown")
if [ "$env_status" = "production" ]; then
    echo -e "${GREEN}✅ Production environment${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  Environment: $env_status${NC}"
fi

# 7. SSL/HTTPS Check
echo -e "\n${YELLOW}🔒 Security Validation${NC}"
echo -e "${YELLOW}---------------------${NC}"

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
echo -n "Checking HTTPS... "
if [[ "$BACKEND_URL" == https://* ]] && [[ "$FRONTEND_URL" == https://* ]]; then
    echo -e "${GREEN}✅ HTTPS enabled${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}❌ HTTPS not enabled${NC}"
fi

# Final Report
echo -e "\n${BLUE}📊 Deployment Validation Results${NC}"
echo -e "${BLUE}================================${NC}"

PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

echo -e "Total Checks: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$((TOTAL_CHECKS - PASSED_CHECKS))${NC}"
echo -e "Pass Rate: ${GREEN}$PASS_RATE%${NC}"

if [ $PASS_RATE -ge 80 ]; then
    echo -e "\n${GREEN}🎉 Deployment is HEALTHY!${NC}"
    echo -e "${GREEN}✅ Your application is ready for production use${NC}"
    exit 0
elif [ $PASS_RATE -ge 60 ]; then
    echo -e "\n${YELLOW}⚠️  Deployment has WARNINGS${NC}"
    echo -e "${YELLOW}🔧 Some issues need attention but app is functional${NC}"
    exit 1
else
    echo -e "\n${RED}🚨 Deployment has CRITICAL ISSUES${NC}"
    echo -e "${RED}❌ Significant problems need immediate attention${NC}"
    exit 2
fi 