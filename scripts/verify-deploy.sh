#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 Running pre-deployment verification...${NC}"

# Check required files exist
required_files=(
    "requirements.txt"
    "app/main.py"
    "app/core/config.py"
    "frontend/next.config.js"
    "render.yaml"
)

echo -e "\n${YELLOW}Checking required files...${NC}"
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ Found $file${NC}"
    else
        echo -e "${RED}❌ Missing $file${NC}"
        exit 1
    fi
done

# Verify backend requirements
echo -e "\n${YELLOW}Checking backend requirements...${NC}"
if grep -q "gunicorn" requirements.txt && grep -q "psycopg2-binary" requirements.txt; then
    echo -e "${GREEN}✓ Found gunicorn and psycopg2-binary in requirements.txt${NC}"
else
    echo -e "${RED}❌ Missing required packages in requirements.txt${NC}"
    exit 1
fi

# Verify health endpoint
echo -e "\n${YELLOW}Checking health endpoint in main.py...${NC}"
if grep -q "@app.get(\"/health\")" app/main.py; then
    echo -e "${GREEN}✓ Found health endpoint${NC}"
else
    echo -e "${RED}❌ Missing health endpoint${NC}"
    exit 1
fi

# Verify frontend configuration
echo -e "\n${YELLOW}Checking frontend configuration...${NC}"
if grep -q "output: 'standalone'" frontend/next.config.js; then
    echo -e "${GREEN}✓ Frontend configured for standalone output${NC}"
else
    echo -e "${RED}❌ Frontend not configured for standalone output${NC}"
    exit 1
fi

# Verify render.yaml
echo -e "\n${YELLOW}Checking render.yaml configuration...${NC}"
if grep -q "gunicorn app.main:app" render.yaml && grep -q "npm run build" render.yaml; then
    echo -e "${GREEN}✓ render.yaml contains required build commands${NC}"
else
    echo -e "${RED}❌ render.yaml missing required build commands${NC}"
    exit 1
fi

# Test backend startup locally (optional)
echo -e "\n${YELLOW}Testing backend startup...${NC}"
echo -e "${YELLOW}⚠️  Skipping import test (will be verified during deployment)${NC}"

# Create deployment checklist
echo -e "\n${YELLOW}📋 Deployment Checklist:${NC}"
echo "1. Render Account Setup:"
echo "  □ GitHub repository connected"
echo "  □ Postgres database created"
echo "  □ Database connection string copied"
echo ""
echo "2. Backend Service:"
echo "  □ Root directory set to: / (root)"
echo "  □ Build command: pip install -r requirements.txt"
echo "  □ Start command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:\$PORT"
echo "  □ Health check path: /health"
echo "  □ Environment variables set:"
echo "    □ DATABASE_URL"
echo "    □ SECRET_KEY"
echo "    □ CORS_ORIGINS"
echo "    □ FRONTEND_URL"
echo ""
echo "3. Frontend Service:"
echo "  □ Root directory set to: frontend/"
echo "  □ Build command: npm install && npm run build"
echo "  □ Start command: npm start"
echo "  □ Environment variables set:"
echo "    □ BACKEND_URL"
echo "    □ NODE_ENV=production"
echo ""
echo "4. Post-Deployment Verification:"
echo "  □ Backend health check responds"
echo "  □ Frontend loads successfully"
echo "  □ API calls work without CORS errors"
echo "  □ Database migrations applied"

echo -e "\n${GREEN}✓ Pre-deployment verification completed${NC}"
echo -e "${YELLOW}⚠️  Remember to set all environment variables in Render dashboard${NC}" 