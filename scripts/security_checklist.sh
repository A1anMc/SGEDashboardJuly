#!/bin/bash

# Security Checklist Script for SGE Dashboard
# This script verifies security configurations after deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL=${1:-"https://sge-dashboard-api.onrender.com"}
FRONTEND_URL=${2:-"https://sge-dashboard-web.onrender.com"}

echo -e "${BLUE}🔒 SGE Dashboard Security Checklist${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Initialize counters
PASSED=0
FAILED=0
WARNINGS=0

# Function to check HTTP headers
check_header() {
    local url=$1
    local header=$2
    local expected=$3
    local description=$4
    
    echo -n "Checking $description... "
    
    if command -v curl >/dev/null 2>&1; then
        actual=$(curl -s -I "$url" | grep -i "$header:" | cut -d' ' -f2- | tr -d '\r\n' || echo "")
        
        if [[ -n "$actual" ]]; then
            if [[ "$expected" == "*" ]] || [[ "$actual" == *"$expected"* ]]; then
                echo -e "${GREEN}✓ PASS${NC} ($actual)"
                ((PASSED++))
            else
                echo -e "${RED}✗ FAIL${NC} (Expected: $expected, Got: $actual)"
                ((FAILED++))
            fi
        else
            echo -e "${RED}✗ FAIL${NC} (Header not found)"
            ((FAILED++))
        fi
    else
        echo -e "${YELLOW}⚠ SKIP${NC} (curl not available)"
        ((WARNINGS++))
    fi
}

# Function to check endpoint response
check_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Checking $description... "
    
    if command -v curl >/dev/null 2>&1; then
        status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        
        if [[ "$status" == "$expected_status" ]]; then
            echo -e "${GREEN}✓ PASS${NC} (Status: $status)"
            ((PASSED++))
        else
            echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status)"
            ((FAILED++))
        fi
    else
        echo -e "${YELLOW}⚠ SKIP${NC} (curl not available)"
        ((WARNINGS++))
    fi
}

# Function to check JSON response
check_json_field() {
    local url=$1
    local field=$2
    local expected=$3
    local description=$4
    
    echo -n "Checking $description... "
    
    if command -v curl >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
        actual=$(curl -s "$url" | jq -r ".$field" 2>/dev/null || echo "null")
        
        if [[ "$actual" == "$expected" ]]; then
            echo -e "${GREEN}✓ PASS${NC} ($actual)"
            ((PASSED++))
        else
            echo -e "${RED}✗ FAIL${NC} (Expected: $expected, Got: $actual)"
            ((FAILED++))
        fi
    else
        echo -e "${YELLOW}⚠ SKIP${NC} (curl or jq not available)"
        ((WARNINGS++))
    fi
}

echo -e "${BLUE}🔍 Backend Security Checks${NC}"
echo "=========================="

# Backend health check
check_endpoint "$BACKEND_URL/health" "200" "Backend health endpoint"

# Backend security headers
check_header "$BACKEND_URL/health" "X-Frame-Options" "DENY" "X-Frame-Options header"
check_header "$BACKEND_URL/health" "X-Content-Type-Options" "nosniff" "X-Content-Type-Options header"
check_header "$BACKEND_URL/health" "Strict-Transport-Security" "max-age" "HSTS header"
check_header "$BACKEND_URL/health" "Content-Security-Policy" "*" "CSP header"

# Backend debug endpoints (should be disabled)
check_endpoint "$BACKEND_URL/api/docs" "404" "API docs disabled in production"
check_endpoint "$BACKEND_URL/api/debug/db" "403" "Debug endpoints disabled"

# Backend environment check
check_json_field "$BACKEND_URL/health" "environment" "production" "Environment set to production"

echo ""
echo -e "${BLUE}🌐 Frontend Security Checks${NC}"
echo "==========================="

# Frontend health check
check_endpoint "$FRONTEND_URL/api/health" "200" "Frontend health endpoint"

# Frontend security headers
check_header "$FRONTEND_URL" "X-Frame-Options" "DENY" "X-Frame-Options header"
check_header "$FRONTEND_URL" "X-Content-Type-Options" "nosniff" "X-Content-Type-Options header"
check_header "$FRONTEND_URL" "Strict-Transport-Security" "max-age" "HSTS header"
check_header "$FRONTEND_URL" "Content-Security-Policy" "*" "CSP header"
check_header "$FRONTEND_URL" "Referrer-Policy" "strict-origin-when-cross-origin" "Referrer-Policy header"

# Check for powered-by header (should be disabled)
echo -n "Checking X-Powered-By header disabled... "
powered_by=$(curl -s -I "$FRONTEND_URL" | grep -i "X-Powered-By:" || echo "")
if [[ -z "$powered_by" ]]; then
    echo -e "${GREEN}✓ PASS${NC} (Header not present)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (Header present: $powered_by)"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}🔐 SSL/TLS Security Checks${NC}"
echo "=========================="

# Check SSL certificate
echo -n "Checking SSL certificate validity... "
if command -v openssl >/dev/null 2>&1; then
    backend_host=$(echo "$BACKEND_URL" | sed 's|https://||' | sed 's|/.*||')
    frontend_host=$(echo "$FRONTEND_URL" | sed 's|https://||' | sed 's|/.*||')
    
    # Check backend SSL
    if echo | openssl s_client -connect "$backend_host:443" -servername "$backend_host" 2>/dev/null | openssl x509 -noout -dates >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC} (Backend SSL valid)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} (Backend SSL invalid)"
        ((FAILED++))
    fi
    
    # Check frontend SSL
    echo -n "Checking frontend SSL certificate... "
    if echo | openssl s_client -connect "$frontend_host:443" -servername "$frontend_host" 2>/dev/null | openssl x509 -noout -dates >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC} (Frontend SSL valid)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} (Frontend SSL invalid)"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC} (openssl not available)"
    ((WARNINGS++))
fi

echo ""
echo -e "${BLUE}🚀 Performance & Availability Checks${NC}"
echo "===================================="

# Check response times
echo -n "Checking backend response time... "
if command -v curl >/dev/null 2>&1; then
    backend_time=$(curl -s -o /dev/null -w "%{time_total}" "$BACKEND_URL/health" || echo "999")
    backend_time_ms=$(echo "$backend_time * 1000" | bc 2>/dev/null || echo "999")
    
    if (( $(echo "$backend_time < 2.0" | bc -l 2>/dev/null || echo "0") )); then
        echo -e "${GREEN}✓ PASS${NC} (${backend_time}s)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ SLOW${NC} (${backend_time}s)"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC} (curl not available)"
    ((WARNINGS++))
fi

echo -n "Checking frontend response time... "
if command -v curl >/dev/null 2>&1; then
    frontend_time=$(curl -s -o /dev/null -w "%{time_total}" "$FRONTEND_URL" || echo "999")
    
    if (( $(echo "$frontend_time < 3.0" | bc -l 2>/dev/null || echo "0") )); then
        echo -e "${GREEN}✓ PASS${NC} (${frontend_time}s)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ SLOW${NC} (${frontend_time}s)"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC} (curl not available)"
    ((WARNINGS++))
fi

echo ""
echo -e "${BLUE}📊 Security Checklist Summary${NC}"
echo "============================="
echo -e "✅ Passed: ${GREEN}$PASSED${NC}"
echo -e "❌ Failed: ${RED}$FAILED${NC}"
echo -e "⚠️  Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

# Overall assessment
TOTAL=$((PASSED + FAILED + WARNINGS))
if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}🎉 Security checklist completed successfully!${NC}"
    echo -e "${GREEN}Your application appears to be properly secured for production.${NC}"
    exit 0
elif [[ $FAILED -le 2 ]]; then
    echo -e "${YELLOW}⚠️  Security checklist completed with minor issues.${NC}"
    echo -e "${YELLOW}Please review the failed checks and address them if possible.${NC}"
    exit 1
else
    echo -e "${RED}❌ Security checklist failed with significant issues.${NC}"
    echo -e "${RED}Please address the failed security checks before going live.${NC}"
    exit 2
fi 