#!/bin/bash

# NavImpact Branding Check Script
# Ensures consistent branding across the project

echo "🔍 Checking NavImpact branding consistency..."

# Check repository name
REPO_URL=$(git config --get remote.origin.url)
if [[ $REPO_URL == *"SGE"* ]] || [[ $REPO_URL == *"sge"* ]]; then
    echo "❌ ERROR: Repository contains old SGE branding: $REPO_URL"
    echo "   Should be: https://github.com/A1anMc/NavImpact.git"
    exit 1
fi

# Check package.json name
if grep -q '"name": "sge' frontend/package.json; then
    echo "❌ ERROR: package.json contains old SGE name"
    exit 1
fi

# Check for SGE references in key files
SGE_FILES=$(grep -r -l -i "sge" --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=venv --exclude=*.log --exclude=*.pyc . | head -5)
if [ ! -z "$SGE_FILES" ]; then
    echo "⚠️  WARNING: Found SGE references in files:"
    echo "$SGE_FILES"
    echo "   Consider updating these to use NavImpact branding"
fi

# Check for NavImpact branding
if grep -q '"name": "navimpact"' frontend/package.json; then
    echo "✅ NavImpact branding found in package.json"
else
    echo "❌ ERROR: NavImpact branding missing from package.json"
    exit 1
fi

echo "✅ Branding check passed!"
echo "🚀 Ready to push to NavImpact repository" 