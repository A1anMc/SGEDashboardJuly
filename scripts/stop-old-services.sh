#!/bin/bash

echo "🔍 CHECKING SERVICE STATUS..."
echo "================================"

echo ""
echo "📡 OLD SERVICES (should be stopped):"
echo "----------------------------------------"
echo "Backend: https://sge-dashboard-api.onrender.com"
curl -s https://sge-dashboard-api.onrender.com/ | jq . 2>/dev/null || echo "❌ Service not responding (good!)"

echo ""
echo "Frontend: https://sge-dashboard-web.onrender.com"
curl -s -I https://sge-dashboard-web.onrender.com/ | head -1 2>/dev/null || echo "❌ Service not responding (good!)"

echo ""
echo "🚀 NEW SERVICES (should be running):"
echo "----------------------------------------"
echo "Backend: https://navimpact-api.onrender.com"
curl -s https://navimpact-api.onrender.com/ | jq . 2>/dev/null || echo "⏳ Service not ready yet"

echo ""
echo "Frontend: https://navimpact-web.onrender.com"
curl -s -I https://navimpact-web.onrender.com/ | head -1 2>/dev/null || echo "⏳ Service not ready yet"

echo ""
echo "✅ EXPECTED RESULT:"
echo "Old services should show 'not responding'"
echo "New services should show NavImpact branding" 