#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load environment variables
if [ -f ".env.production" ]; then
    source .env.production
fi

# Check required environment variables
echo -e "${YELLOW}Checking environment variables...${NC}"
required_vars=("BACKEND_URL" "FRONTEND_URL" "DATABASE_URL" "SECRET_KEY")
missing_vars=0

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Missing required environment variable: ${var}${NC}"
        missing_vars=$((missing_vars + 1))
    else
        echo -e "${GREEN}✓ ${var} is set${NC}"
    fi
done

if [ $missing_vars -gt 0 ]; then
    echo -e "${RED}Error: Missing required environment variables${NC}"
    exit 1
fi

# Function to check endpoint health
check_health() {
    local url=$1
    local name=$2
    echo -e "\n${YELLOW}Checking ${name} health...${NC}"
    
    if curl -f -s "${url}/health" > /dev/null; then
        echo -e "${GREEN}✓ ${name} is healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ ${name} health check failed${NC}"
        return 1
    fi
}

# Check backend health
check_health "${BACKEND_URL}" "Backend"

# Check frontend health
check_health "${FRONTEND_URL}" "Frontend"

# Check database connection through backend
echo -e "\n${YELLOW}Checking database connection...${NC}"
db_health=$(curl -s "${BACKEND_URL}/health")
if echo "$db_health" | grep -q "database.*connected"; then
    echo -e "${GREEN}✓ Database is connected${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    echo "Response: $db_health"
    exit 1
fi

# Check CORS configuration
echo -e "\n${YELLOW}Checking CORS configuration...${NC}"
cors_check=$(curl -I -s -X OPTIONS "${BACKEND_URL}/api/v1/health" \
    -H "Origin: ${FRONTEND_URL}" \
    -H "Access-Control-Request-Method: GET")

if echo "$cors_check" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✓ CORS is properly configured${NC}"
else
    echo -e "${RED}❌ CORS configuration issue detected${NC}"
    echo "Response headers:"
    echo "$cors_check"
    exit 1
fi

echo -e "\n${GREEN}✓ All checks passed successfully!${NC}" 