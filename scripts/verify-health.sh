#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}

# Function to check basic health
check_basic_health() {
    local url=$1
    local name=$2
    echo -e "\n${YELLOW}Checking ${name} basic health...${NC}"
    
    response=$(curl -s "${url}/health")
    status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$status" = "ok" ] || [ "$status" = "healthy" ]; then
        echo -e "${GREEN}✓ ${name} basic health check passed${NC}"
        echo "Response: $response"
        return 0
    else
        echo -e "${RED}❌ ${name} basic health check failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Function to check detailed health
check_detailed_health() {
    local url=$1
    local name=$2
    echo -e "\n${YELLOW}Checking ${name} detailed health...${NC}"
    
    response=$(curl -s "${url}/health/detailed")
    status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$status" = "healthy" ]; then
        echo -e "${GREEN}✓ ${name} detailed health check passed${NC}"
        echo "Response: $response"
        return 0
    else
        echo -e "${RED}❌ ${name} detailed health check failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Function to check CORS
check_cors() {
    local url=$1
    local origin=$2
    echo -e "\n${YELLOW}Checking CORS configuration for ${origin}...${NC}"
    
    response=$(curl -I -s -X OPTIONS "${url}/health" \
        -H "Origin: ${origin}" \
        -H "Access-Control-Request-Method: GET")
    
    if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
        echo -e "${GREEN}✓ CORS is properly configured for ${origin}${NC}"
        return 0
    else
        echo -e "${RED}❌ CORS configuration issue for ${origin}${NC}"
        echo "Response headers:"
        echo "$response"
        return 1
    fi
}

# Check backend health
echo -e "${YELLOW}Testing Backend Health Checks${NC}"
echo "Backend URL: $BACKEND_URL"

check_basic_health "$BACKEND_URL" "Backend"
check_detailed_health "$BACKEND_URL" "Backend"

# Check frontend health
echo -e "\n${YELLOW}Testing Frontend Health Checks${NC}"
echo "Frontend URL: $FRONTEND_URL"

check_basic_health "$FRONTEND_URL/api" "Frontend"

# Check CORS configuration
echo -e "\n${YELLOW}Testing CORS Configuration${NC}"
check_cors "$BACKEND_URL" "$FRONTEND_URL"
check_cors "$BACKEND_URL" "http://localhost:3000"

# Final summary
echo -e "\n${GREEN}✓ Health check verification completed${NC}" 