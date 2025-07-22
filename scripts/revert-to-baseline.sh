#!/bin/bash

# 🛡️ NavImpact Baseline Recovery Script
# This script reverts the system to the last known working state

echo "🛡️ NavImpact Baseline Recovery Script"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "BASELINE_STATUS.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📋 Current status:"
echo "- Frontend: https://navimpact-web.onrender.com"
echo "- Backend: https://navimpact-api.onrender.com"
echo ""

# Ask for confirmation
read -p "⚠️  This will revert to the last working baseline. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Recovery cancelled"
    exit 1
fi

echo "🔄 Starting recovery process..."

# 1. Revert critical frontend files
echo "📱 Reverting frontend files..."
git checkout baseline-working-grants -- frontend/src/app/\(dashboard\)/grants/page.tsx
git checkout baseline-working-grants -- frontend/next.config.js
git checkout baseline-working-grants -- frontend/src/lib/config.ts

# 2. Revert critical backend files
echo "🔧 Reverting backend files..."
git checkout baseline-working-grants -- app/api/v1/endpoints/grants.py
git checkout baseline-working-grants -- app/schemas/grant.py
git checkout baseline-working-grants -- app/models/grant.py

# 3. Commit the recovery
echo "💾 Committing recovery changes..."
git add .
git commit -m "RECOVERY: Reverted to working baseline - grants system functional"

# 4. Push to trigger deployment
echo "🚀 Pushing to trigger deployment..."
git push origin main

echo ""
echo "✅ Recovery completed!"
echo ""
echo "📋 Next steps:"
echo "1. Wait for deployment to complete (2-3 minutes)"
echo "2. Test the grants page: https://navimpact-web.onrender.com/grants"
echo "3. Verify API is working: https://navimpact-api.onrender.com/api/v1/grants/"
echo ""
echo "🔍 If issues persist:"
echo "- Check deployment logs on Render"
echo "- Review BASELINE_STATUS.md for known working configurations"
echo "- Contact development team"
echo ""
echo "🛡️ Baseline protection active!" 