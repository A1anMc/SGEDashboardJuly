#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}🚨 EMERGENCY ROLLBACK PLAN${NC}"
echo -e "${RED}===========================${NC}"

# Check what type of rollback is needed
echo -e "\n${YELLOW}🔍 What type of issue are you experiencing?${NC}"
echo "1. Backend deployment failed"
echo "2. Frontend deployment failed"
echo "3. Database migration failed"
echo "4. Complete system failure"
echo "5. Performance issues"
echo "6. Security breach"

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo -e "\n${YELLOW}🔧 Backend Rollback Procedure${NC}"
        echo -e "${YELLOW}-----------------------------${NC}"
        
        echo -e "\n${BLUE}Immediate Actions:${NC}"
        echo "1. Go to Render Dashboard: https://dashboard.render.com/web/sge-dashboard-api"
        echo "2. Click 'Deploys' tab"
        echo "3. Find the last working deployment"
        echo "4. Click 'Redeploy' on that version"
        
        echo -e "\n${BLUE}Alternative - Manual Rollback:${NC}"
        echo "1. Disable auto-deploy: Settings → Auto-Deploy → OFF"
        echo "2. Check logs for specific error"
        echo "3. Fix the issue locally"
        echo "4. Push fix to GitHub"
        echo "5. Manually trigger deploy"
        
        echo -e "\n${BLUE}Emergency Contact:${NC}"
        echo "- Check backend logs: https://dashboard.render.com/web/sge-dashboard-api/logs"
        echo "- Test health endpoint: curl https://sge-dashboard-api.onrender.com/health"
        ;;
        
    2)
        echo -e "\n${YELLOW}🎨 Frontend Rollback Procedure${NC}"
        echo -e "${YELLOW}------------------------------${NC}"
        
        echo -e "\n${BLUE}Immediate Actions:${NC}"
        echo "1. Go to Render Dashboard: https://dashboard.render.com/web/sge-dashboard-web"
        echo "2. Click 'Deploys' tab"
        echo "3. Find the last working deployment"
        echo "4. Click 'Redeploy' on that version"
        
        echo -e "\n${BLUE}Quick Fix Options:${NC}"
        echo "1. Check build logs for Node.js version issues"
        echo "2. Verify environment variables are set correctly"
        echo "3. Test build locally: cd frontend && npm run build"
        echo "4. Check Next.js configuration"
        
        echo -e "\n${BLUE}Temporary Workaround:${NC}"
        echo "- Deploy a simple static page while fixing main issue"
        echo "- Use maintenance mode HTML"
        ;;
        
    3)
        echo -e "\n${YELLOW}🗄️ Database Rollback Procedure${NC}"
        echo -e "${YELLOW}-------------------------------${NC}"
        
        echo -e "\n${RED}⚠️ CRITICAL: Database rollbacks are dangerous!${NC}"
        
        echo -e "\n${BLUE}Immediate Actions:${NC}"
        echo "1. Check database logs in Render dashboard"
        echo "2. Connect to database directly:"
        echo "   psql \$DATABASE_URL"
        echo "3. Check if tables exist:"
        echo "   \\dt"
        
        echo -e "\n${BLUE}Migration Rollback:${NC}"
        echo "1. Connect to your server/container"
        echo "2. Run: alembic downgrade -1"
        echo "3. Or specific version: alembic downgrade <revision>"
        echo "4. Check migration history: alembic history"
        
        echo -e "\n${RED}Nuclear Option (DATA LOSS):${NC}"
        echo "1. Delete and recreate database in Render"
        echo "2. Update DATABASE_URL in backend service"
        echo "3. Run fresh migrations"
        echo "4. Restore from backup if available"
        ;;
        
    4)
        echo -e "\n${RED}🚨 COMPLETE SYSTEM FAILURE${NC}"
        echo -e "${RED}---------------------------${NC}"
        
        echo -e "\n${BLUE}Emergency Checklist:${NC}"
        echo "□ Check Render status page: https://status.render.com"
        echo "□ Verify all services are running in dashboard"
        echo "□ Check database connectivity"
        echo "□ Test health endpoints"
        echo "□ Review recent deployments"
        
        echo -e "\n${BLUE}Recovery Steps:${NC}"
        echo "1. Disable auto-deploy on all services"
        echo "2. Roll back to last known good deployment"
        echo "3. Check environment variables"
        echo "4. Verify database connection strings"
        echo "5. Test each service individually"
        
        echo -e "\n${BLUE}Communication:${NC}"
        echo "- Post status update to users"
        echo "- Document the incident"
        echo "- Prepare post-mortem analysis"
        ;;
        
    5)
        echo -e "\n${YELLOW}⚡ Performance Issues${NC}"
        echo -e "${YELLOW}--------------------${NC}"
        
        echo -e "\n${BLUE}Quick Fixes:${NC}"
        echo "1. Scale up backend workers in Render"
        echo "2. Check database connection pool settings"
        echo "3. Review recent code changes"
        echo "4. Monitor resource usage"
        
        echo -e "\n${BLUE}Monitoring Commands:${NC}"
        echo "- Backend health: curl https://sge-dashboard-api.onrender.com/health/detailed"
        echo "- Database status: Check Render dashboard metrics"
        echo "- Frontend performance: Check browser dev tools"
        ;;
        
    6)
        echo -e "\n${RED}🔒 SECURITY BREACH${NC}"
        echo -e "${RED}------------------${NC}"
        
        echo -e "\n${RED}IMMEDIATE ACTIONS:${NC}"
        echo "1. DISABLE AUTO-DEPLOY immediately"
        echo "2. Change all passwords and API keys"
        echo "3. Rotate SECRET_KEY in environment variables"
        echo "4. Review access logs"
        echo "5. Check for unauthorized database access"
        
        echo -e "\n${BLUE}Recovery Steps:${NC}"
        echo "1. Audit all environment variables"
        echo "2. Review recent commits for malicious code"
        echo "3. Check database for unauthorized changes"
        echo "4. Update all dependencies"
        echo "5. Enable additional security measures"
        
        echo -e "\n${BLUE}Post-Incident:${NC}"
        echo "- Document the breach"
        echo "- Notify affected users"
        echo "- Implement additional security measures"
        ;;
        
    *)
        echo -e "\n${RED}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo -e "\n${BLUE}📞 Additional Resources:${NC}"
echo "- Render Support: https://render.com/support"
echo "- Documentation: https://render.com/docs"
echo "- Status Page: https://status.render.com"
echo "- Community: https://community.render.com"

echo -e "\n${YELLOW}🔧 Useful Commands:${NC}"
echo "- Check backend health: ./scripts/check-backend-health.sh"
echo "- Validate deployment: ./scripts/validate-deployment.sh"
echo "- View logs: render logs follow <service-name>"

echo -e "\n${GREEN}📝 Remember to document the incident and implement preventive measures!${NC}" 