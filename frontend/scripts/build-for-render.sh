#!/bin/bash

# Build script for Render deployment
# This script handles common Next.js standalone issues

set -e  # Exit on any error

echo "🚀 Starting build for Render deployment..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf .next
rm -rf node_modules/.cache

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --only=production --no-audit

# Build the application
echo "🔨 Building Next.js application..."
npm run build

# Verify standalone server exists
if [ ! -f ".next/standalone/server.js" ]; then
    echo "❌ ERROR: standalone server.js not found!"
    echo "Build failed - standalone output not generated"
    exit 1
fi

# Create necessary directories
echo "📁 Setting up standalone directory structure..."
mkdir -p .next/standalone/.next

# Copy static assets
echo "📋 Copying static assets..."
if [ -d ".next/static" ]; then
    cp -r .next/static .next/standalone/.next/
    echo "✅ Static assets copied successfully"
else
    echo "⚠️  Warning: .next/static directory not found"
fi

# Copy public assets
echo "📋 Copying public assets..."
if [ -d "public" ]; then
    cp -r public .next/standalone/
    echo "✅ Public assets copied successfully"
else
    echo "⚠️  Warning: public directory not found"
fi

# Verify the build
echo "🔍 Verifying build..."
if [ -f ".next/standalone/server.js" ]; then
    echo "✅ Standalone server.js exists"
else
    echo "❌ ERROR: server.js missing after build"
    exit 1
fi

if [ -d ".next/standalone/.next/static" ]; then
    echo "✅ Static assets in place"
else
    echo "⚠️  Warning: Static assets not found in standalone"
fi

if [ -d ".next/standalone/public" ]; then
    echo "✅ Public assets in place"
else
    echo "⚠️  Warning: Public assets not found in standalone"
fi

echo "🎉 Build completed successfully!"
echo "📊 Build size:"
du -sh .next/standalone

echo "🚀 Ready for deployment!" 