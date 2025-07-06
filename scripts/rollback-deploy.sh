#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧯 Deployment Rollback Preparation${NC}"
echo -e "${BLUE}===================================${NC}"

# Create rollback directory
ROLLBACK_DIR="rollback-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$ROLLBACK_DIR"

echo -e "\n${YELLOW}📁 Created rollback directory: $ROLLBACK_DIR${NC}"

# Archive current environment variables
echo -e "\n${YELLOW}📋 Archiving current environment variables...${NC}"

# Backend environment variables
echo -e "\n${BLUE}🔧 Backend Environment Variables:${NC}"
cat > "$ROLLBACK_DIR/backend-env-vars.txt" << EOF
# Backend Environment Variables - $(date)
# Service: sge-dashboard-api
DATABASE_URL=<your-current-database-url>
SECRET_KEY=<your-current-secret-key>
CORS_ORIGINS=https://sge-dashboard.onrender.com
FRONTEND_URL=https://sge-dashboard.onrender.com
ENVIRONMENT=production
EOF

echo -e "${GREEN}✅ Backend env vars archived${NC}"

# Frontend environment variables
echo -e "\n${BLUE}🎨 Frontend Environment Variables:${NC}"
cat > "$ROLLBACK_DIR/frontend-env-vars.txt" << EOF
# Frontend Environment Variables - $(date)
# Service: sge-dashboard
BACKEND_URL=https://sge-dashboard-api.onrender.com
NODE_ENV=production
EOF

echo -e "${GREEN}✅ Frontend env vars archived${NC}"

# Create emergency .env.rollback file
echo -e "\n${YELLOW}🚨 Creating emergency .env.rollback file...${NC}"
cat > ".env.rollback" << EOF
# Emergency Rollback Environment - $(date)
# Use this file to quickly restore local development environment

# Database (local SQLite for emergency testing)
DATABASE_URL=sqlite:///./emergency.db

# Security
SECRET_KEY=emergency-secret-key-change-immediately

# CORS (local development)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# URLs (local development)
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Environment
ENVIRONMENT=development
DEBUG=true

# Email (disabled for emergency)
SENDGRID_API_KEY=disabled
FROM_EMAIL=noreply@localhost

# Database Pool (reduced for local)
DATABASE_POOL_SIZE=1
DATABASE_MAX_OVERFLOW=2
EOF

echo -e "${GREEN}✅ Emergency .env.rollback created${NC}"

# Get current Git commit SHA
if git rev-parse --git-dir > /dev/null 2>&1; then
    CURRENT_COMMIT=$(git rev-parse HEAD)
    CURRENT_BRANCH=$(git branch --show-current)
    
    echo -e "\n${YELLOW}📝 Recording current Git state...${NC}"
    cat > "$ROLLBACK_DIR/git-state.txt" << EOF
# Git State - $(date)
Current Branch: $CURRENT_BRANCH
Current Commit: $CURRENT_COMMIT
Commit Message: $(git log -1 --pretty=format:"%s")
Commit Author: $(git log -1 --pretty=format:"%an")
Commit Date: $(git log -1 --pretty=format:"%ad")

# To rollback to this commit:
# git checkout $CURRENT_COMMIT
# git checkout -b rollback-$(date +%Y%m%d-%H%M%S)
EOF

    echo -e "${GREEN}✅ Git state recorded${NC}"
    echo -e "${BLUE}Current commit: $CURRENT_COMMIT${NC}"
    echo -e "${BLUE}Current branch: $CURRENT_BRANCH${NC}"
else
    echo -e "${YELLOW}⚠️  Not in a Git repository${NC}"
fi

# Create rollback instructions
echo -e "\n${YELLOW}📖 Creating rollback instructions...${NC}"
cat > "$ROLLBACK_DIR/ROLLBACK_INSTRUCTIONS.md" << EOF
# 🚨 Emergency Rollback Instructions

## Quick Rollback Steps

### 1. Render Dashboard Rollback
1. Go to [Render Dashboard](https://dashboard.render.com)
2. **Backend**: https://dashboard.render.com/web/sge-dashboard-api
   - Click "Deploys" tab
   - Find last working deployment
   - Click "Redeploy"
3. **Frontend**: https://dashboard.render.com/web/sge-dashboard
   - Click "Deploys" tab
   - Find last working deployment
   - Click "Redeploy"

### 2. Environment Variables Restore
- Backend vars: See \`backend-env-vars.txt\`
- Frontend vars: See \`frontend-env-vars.txt\`

### 3. Git Rollback (if needed)
\`\`\`bash
# See current state in git-state.txt
git checkout <commit-sha>
git checkout -b emergency-rollback-$(date +%Y%m%d)
\`\`\`

### 4. Local Emergency Environment
\`\`\`bash
# Copy emergency environment
cp .env.rollback .env

# Start local services
make dev  # or your preferred method
\`\`\`

### 5. Database Emergency
If database is corrupted:
1. Use local SQLite: \`DATABASE_URL=sqlite:///./emergency.db\`
2. Run migrations: \`alembic upgrade head\`
3. Restore from backup if available

## Verification Commands
\`\`\`bash
# Check backend health
curl https://sge-dashboard-api.onrender.com/health

# Check frontend
curl https://sge-dashboard.onrender.com

# Validate full deployment
./scripts/validate-deployment.sh
\`\`\`

## Contact Information
- Render Support: https://render.com/support
- Status Page: https://status.render.com
- Documentation: https://render.com/docs

---
Created: $(date)
Rollback Directory: $ROLLBACK_DIR
EOF

echo -e "${GREEN}✅ Rollback instructions created${NC}"

# Create verification script
echo -e "\n${YELLOW}🧪 Creating rollback verification script...${NC}"
cat > "$ROLLBACK_DIR/verify-rollback.sh" << 'EOF'
#!/bin/bash
set -e

echo "🔍 Verifying rollback success..."

# Check backend
echo -n "Backend health check... "
if curl -s https://sge-dashboard-api.onrender.com/health > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

# Check frontend
echo -n "Frontend check... "
if curl -s https://sge-dashboard.onrender.com > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🎉 Rollback verification successful!"
EOF

chmod +x "$ROLLBACK_DIR/verify-rollback.sh"
echo -e "${GREEN}✅ Verification script created${NC}"

# Final summary
echo -e "\n${BLUE}📊 Rollback Preparation Complete${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "Rollback Directory: ${YELLOW}$ROLLBACK_DIR${NC}"
echo -e "Emergency Environment: ${YELLOW}.env.rollback${NC}"
echo -e "Instructions: ${YELLOW}$ROLLBACK_DIR/ROLLBACK_INSTRUCTIONS.md${NC}"
echo -e "Verification: ${YELLOW}$ROLLBACK_DIR/verify-rollback.sh${NC}"

echo -e "\n${GREEN}🎯 Next Steps:${NC}"
echo "1. Review the rollback instructions"
echo "2. Keep this directory safe for emergency use"
echo "3. Proceed with your deployment"
echo "4. If issues occur, follow the rollback instructions"

echo -e "\n${YELLOW}⚠️  Remember: Test your deployment thoroughly before going live!${NC}" 