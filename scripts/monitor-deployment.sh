#!/bin/bash

# Deployment Monitor Script for SGE Dashboard
# Monitors deployment progress and provides real-time feedback

echo "📡 SGE Dashboard Deployment Monitor"
echo "===================================="

# Configuration
BACKEND_URL="https://sge-dashboard-api.onrender.com"
FRONTEND_URL="https://sge-dashboard-web.onrender.com"
CHECK_INTERVAL=15  # seconds between checks
MAX_CHECKS=40      # maximum number of checks (10 minutes)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check service status
check_service() {
    local url=$1
    local service_name=$2
    
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url")
    
    case $status_code in
        200)
            echo -e "${GREEN}✓ $service_name: HEALTHY${NC}"
            return 0
            ;;
        503)
            echo -e "${RED}✗ $service_name: SERVICE UNAVAILABLE${NC}"
            return 1
            ;;
        000)
            echo -e "${YELLOW}⏳ $service_name: DEPLOYING/TIMEOUT${NC}"
            return 2
            ;;
        *)
            echo -e "${RED}⚠ $service_name: ERROR ($status_code)${NC}"
            return 1
            ;;
    esac
}

# Function to get timestamp
get_timestamp() {
    date '+%H:%M:%S'
}

# Main monitoring loop
echo "Starting deployment monitoring..."
echo "Checking every $CHECK_INTERVAL seconds for up to $((MAX_CHECKS * CHECK_INTERVAL / 60)) minutes"
echo ""

backend_healthy=false
frontend_healthy=false
check_count=0

while [ $check_count -lt $MAX_CHECKS ]; do
    timestamp=$(get_timestamp)
    echo -e "${BLUE}[$timestamp] Check #$((check_count + 1))${NC}"
    
    # Check backend
    if check_service "$BACKEND_URL/health" "Backend"; then
        if [ "$backend_healthy" = false ]; then
            echo -e "${GREEN}🎉 Backend deployment successful!${NC}"
            backend_healthy=true
        fi
    else
        backend_healthy=false
    fi
    
    # Check frontend
    if check_service "$FRONTEND_URL" "Frontend"; then
        if [ "$frontend_healthy" = false ]; then
            echo -e "${GREEN}🎉 Frontend deployment successful!${NC}"
            frontend_healthy=true
        fi
    else
        frontend_healthy=false
    fi
    
    # Check if both services are healthy
    if [ "$backend_healthy" = true ] && [ "$frontend_healthy" = true ]; then
        echo ""
        echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
        echo -e "${GREEN}Both services are healthy and responding${NC}"
        echo ""
        echo "🔗 URLs:"
        echo "Frontend: $FRONTEND_URL"
        echo "Backend:  $BACKEND_URL"
        echo ""
        echo "Running full health check..."
        ./scripts/production-health-check.sh
        exit 0
    fi
    
    check_count=$((check_count + 1))
    
    if [ $check_count -lt $MAX_CHECKS ]; then
        echo "Waiting ${CHECK_INTERVAL}s for next check..."
        echo ""
        sleep $CHECK_INTERVAL
    fi
done

# Timeout reached
echo ""
echo -e "${RED}⏰ Monitoring timeout reached${NC}"
echo "Deployment may still be in progress. Check Render dashboard for details."
echo ""
echo "Final status check:"
./scripts/production-health-check.sh 