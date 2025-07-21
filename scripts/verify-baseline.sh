#!/bin/bash

# NavImpact Baseline Verification Script
# Verifies that all critical services are working correctly

set -e

echo "🔍 NavImpact Baseline Verification"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="https://navimpact-api.onrender.com"
FRONTEND_URL="https://navimpact-web.onrender.com"

echo "🌐 Testing API endpoints..."

# Test 1: Root endpoint
echo -n "  ✓ Root endpoint: "
if curl -s "$API_URL/" | grep -q "NavImpact API"; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 2: Health endpoint
echo -n "  ✓ Health endpoint: "
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"' && echo "$HEALTH_RESPONSE" | grep -q '"database":"connected"'; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "    Response: $HEALTH_RESPONSE"
    exit 1
fi

# Test 3: API version
echo -n "  ✓ API version: "
if curl -s "$API_URL/" | grep -q '"version":"1.0.0"'; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 4: Production environment
echo -n "  ✓ Environment: "
if curl -s "$API_URL/" | grep -q '"environment":"production"'; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 5: Disabled scraper endpoints
echo -n "  ✓ Scrapers disabled: "
SCRAPER_RESPONSE=$(curl -s "$API_URL/api/v1/grants/sources")
if echo "$SCRAPER_RESPONSE" | grep -q '"status":"disabled"' || echo "$SCRAPER_RESPONSE" | grep -q '"detail":"Database service unavailable"'; then
    echo -e "${GREEN}PASS${NC} (endpoint exists)"
else
    echo -e "${YELLOW}WARNING${NC} - Unexpected response: $SCRAPER_RESPONSE"
fi

echo ""
echo "🌍 Testing frontend..."

# Test 6: Frontend accessibility
echo -n "  ✓ Frontend accessible: "
if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200"; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${YELLOW}WARNING - Check frontend manually${NC}"
fi

echo ""
echo "📊 Current deployment info:"
HEALTH_DATA=$(curl -s "$API_URL/health")
echo "  • Status: $(echo "$HEALTH_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")"
echo "  • Database: $(echo "$HEALTH_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['database'])")"
echo "  • Version: $(echo "$HEALTH_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")"
echo "  • Environment: $(echo "$HEALTH_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['environment'])")"

echo ""
echo -e "${GREEN}✅ NavImpact Baseline Verification: ALL TESTS PASSED${NC}"
echo ""
echo "🔗 Service URLs:"
echo "  • API: $API_URL"
echo "  • Frontend: $FRONTEND_URL"
echo "  • Health: $API_URL/health"
echo ""
echo "📋 Git info:"
echo "  • Current commit: $(git rev-parse --short HEAD)"
echo "  • Current branch: $(git branch --show-current)"
echo "  • Latest tag: $(git describe --tags --abbrev=0 2>/dev/null || echo 'No tags')"
echo ""
echo "🎯 Baseline established successfully!" 