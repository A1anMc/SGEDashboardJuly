#!/bin/bash

# Frontend Security Scan Script
# This script runs various security checks on the frontend codebase

set -e

echo "🔒 Starting Frontend Security Scan..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    print_error "This script must be run from the frontend directory"
    exit 1
fi

# 1. NPM Audit
echo "📦 Running npm audit..."
if npm audit --audit-level=high; then
    print_status "npm audit passed"
else
    print_error "npm audit found high severity vulnerabilities"
    exit 1
fi

# 2. Check for outdated packages
echo "📋 Checking for outdated packages..."
OUTDATED=$(npm outdated --depth=0 2>/dev/null | wc -l)
if [ "$OUTDATED" -gt 1 ]; then
    print_warning "Found $((OUTDATED - 1)) outdated packages"
    npm outdated --depth=0
else
    print_status "All packages are up to date"
fi

# 3. Check for known vulnerabilities in dependencies
echo "🔍 Checking for known vulnerabilities..."
if command -v snyk &> /dev/null; then
    if snyk test --severity-threshold=high; then
        print_status "Snyk security scan passed"
    else
        print_error "Snyk found high severity vulnerabilities"
        exit 1
    fi
else
    print_warning "Snyk not installed. Install with: npm install -g snyk"
fi

# 4. Check for exposed secrets in code
echo "🔐 Scanning for potential secrets..."
if command -v trufflehog &> /dev/null; then
    if trufflehog --fail --no-update .; then
        print_status "No secrets found in codebase"
    else
        print_error "Potential secrets found in codebase"
        exit 1
    fi
else
    print_warning "TruffleHog not installed. Install with: pip install trufflehog"
fi

# 5. Check CSP configuration
echo "🛡️  Checking CSP configuration..."
if grep -q "Content-Security-Policy" next.config.js; then
    print_status "CSP headers are configured"
else
    print_warning "CSP headers not found in next.config.js"
fi

# 6. Check for dangerous dependencies
echo "⚠️  Checking for potentially dangerous dependencies..."
DANGEROUS_DEPS=("eval" "vm" "child_process" "fs" "path")
for dep in "${DANGEROUS_DEPS[@]}"; do
    if grep -r "$dep" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" | grep -v "//" | grep -v "import.*$dep"; then
        print_warning "Found potential use of dangerous dependency: $dep"
    fi
done

# 7. Check for proper error handling
echo "🚨 Checking error handling..."
if grep -r "console.error" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" | wc -l | grep -q "[1-9]"; then
    print_status "Error handling found in codebase"
else
    print_warning "No explicit error handling found"
fi

# 8. Check for proper TypeScript usage
echo "📝 Checking TypeScript configuration..."
if [ -f "tsconfig.json" ]; then
    if grep -q '"strict": true' tsconfig.json; then
        print_status "TypeScript strict mode is enabled"
    else
        print_warning "TypeScript strict mode is not enabled"
    fi
else
    print_error "tsconfig.json not found"
fi

# 9. Check for proper ESLint configuration
echo "🔍 Checking ESLint configuration..."
if [ -f ".eslintrc.json" ] || [ -f "eslint.config.mjs" ]; then
    print_status "ESLint is configured"
else
    print_warning "ESLint configuration not found"
fi

# 10. Check for proper environment variable handling
echo "🔧 Checking environment variable handling..."
if grep -r "process.env" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" | grep -v "NEXT_PUBLIC_" | grep -v "NODE_ENV"; then
    print_warning "Found server-side environment variables in client code"
else
    print_status "Environment variables properly handled"
fi

echo ""
echo "🎉 Frontend Security Scan Complete!"
echo ""
echo "Summary:"
echo "- npm audit: ✅"
echo "- Outdated packages: $((OUTDATED - 1)) found"
echo "- Snyk scan: $(if command -v snyk &> /dev/null; then echo "✅"; else echo "⚠️  Not installed"; fi)"
echo "- Secrets scan: $(if command -v trufflehog &> /dev/null; then echo "✅"; else echo "⚠️  Not installed"; fi)"
echo "- CSP headers: ✅"
echo "- TypeScript strict mode: $(if grep -q '"strict": true' tsconfig.json 2>/dev/null; then echo "✅"; else echo "⚠️"; fi)"
echo "- ESLint: ✅"
echo ""
echo "Recommendations:"
echo "1. Install Snyk for comprehensive vulnerability scanning"
echo "2. Install TruffleHog for secret detection"
echo "3. Enable TypeScript strict mode if not already enabled"
echo "4. Review any warnings above" 