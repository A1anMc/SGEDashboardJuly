#!/bin/bash

# Full-Stack Deployment Script
# Usage: ./scripts/deploy.sh [backend|frontend|both]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/your-username/your-repo.git"
BACKEND_URL="https://your-app-backend.onrender.com"
FRONTEND_URL="https://your-app-frontend.onrender.com"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        warning "You have uncommitted changes. Consider committing them first."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check if we're on main branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        warning "You're not on main/master branch (currently on $current_branch)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    success "Pre-deployment checks passed"
}

# Backend deployment
deploy_backend() {
    log "Starting backend deployment..."
    
    # Check if backend health endpoint exists
    if ! grep -q "health" app/api/v1/endpoints/health.py 2>/dev/null; then
        error "Backend health endpoint not found. Please implement /health endpoint."
        exit 1
    fi
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        error "requirements.txt not found"
        exit 1
    fi
    
    # Check if main.py exists
    if [ ! -f "app/main.py" ]; then
        error "app/main.py not found"
        exit 1
    fi
    
    success "Backend validation passed"
}

# Frontend deployment
deploy_frontend() {
    log "Starting frontend deployment..."
    
    # Check if frontend directory exists
    if [ ! -d "frontend" ]; then
        error "frontend directory not found"
        exit 1
    fi
    
    # Check if package.json exists
    if [ ! -f "frontend/package.json" ]; then
        error "frontend/package.json not found"
        exit 1
    fi
    
    # Check if next.config.js exists
    if [ ! -f "frontend/next.config.js" ]; then
        error "frontend/next.config.js not found"
        exit 1
    fi
    
    # Check if build script exists
    if ! grep -q '"build"' frontend/package.json; then
        error "Build script not found in package.json"
        exit 1
    fi
    
    success "Frontend validation passed"
}

# Push to GitHub
push_to_github() {
    log "Pushing to GitHub..."
    
    # Add all changes
    git add .
    
    # Create commit
    commit_message="Deploy: $(date +'%Y-%m-%d %H:%M:%S')"
    git commit -m "$commit_message"
    
    # Push to main branch
    git push origin main
    
    success "Code pushed to GitHub"
}

# Wait for deployment
wait_for_deployment() {
    local service_name=$1
    local health_url=$2
    local max_attempts=30
    local attempt=1
    
    log "Waiting for $service_name deployment..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$health_url" > /dev/null 2>&1; then
            success "$service_name is live at $health_url"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 30
        ((attempt++))
    done
    
    error "$service_name deployment failed or timed out"
    return 1
}

# Test deployment
test_deployment() {
    local service_name=$1
    local url=$2
    
    log "Testing $service_name deployment..."
    
    # Test basic connectivity
    if curl -s -f "$url" > /dev/null 2>&1; then
        success "$service_name is responding"
    else
        error "$service_name is not responding"
        return 1
    fi
    
    # Test health endpoint if it's the backend
    if [ "$service_name" = "backend" ]; then
        if curl -s -f "$url/health" > /dev/null 2>&1; then
            success "Backend health check passed"
        else
            error "Backend health check failed"
            return 1
        fi
    fi
}

# Main deployment function
main() {
    local target=${1:-"both"}
    
    log "Starting deployment for: $target"
    
    # Pre-deployment checks
    pre_deployment_checks
    
    # Validate based on target
    case $target in
        "backend")
            deploy_backend
            ;;
        "frontend")
            deploy_frontend
            ;;
        "both")
            deploy_backend
            deploy_frontend
            ;;
        *)
            error "Invalid target: $target. Use: backend, frontend, or both"
            exit 1
            ;;
    esac
    
    # Push to GitHub
    push_to_github
    
    # Wait for deployment based on target
    case $target in
        "backend")
            wait_for_deployment "Backend" "$BACKEND_URL/health"
            test_deployment "backend" "$BACKEND_URL"
            ;;
        "frontend")
            wait_for_deployment "Frontend" "$FRONTEND_URL"
            test_deployment "frontend" "$FRONTEND_URL"
            ;;
        "both")
            wait_for_deployment "Backend" "$BACKEND_URL/health"
            test_deployment "backend" "$BACKEND_URL"
            
            wait_for_deployment "Frontend" "$FRONTEND_URL"
            test_deployment "frontend" "$FRONTEND_URL"
            ;;
    esac
    
    success "Deployment completed successfully!"
    
    # Print URLs
    echo
    log "Deployment URLs:"
    echo "Backend: $BACKEND_URL"
    echo "Frontend: $FRONTEND_URL"
    echo
    log "Monitor deployment at: https://dashboard.render.com"
}

# Help function
show_help() {
    echo "Usage: $0 [backend|frontend|both]"
    echo
    echo "Options:"
    echo "  backend   - Deploy only the backend"
    echo "  frontend  - Deploy only the frontend"
    echo "  both      - Deploy both backend and frontend (default)"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  $0              # Deploy both services"
    echo "  $0 backend      # Deploy only backend"
    echo "  $0 frontend     # Deploy only frontend"
}

# Parse command line arguments
case ${1:-"both"} in
    "help"|"-h"|"--help")
        show_help
        exit 0
        ;;
    "backend"|"frontend"|"both")
        main "$1"
        ;;
    *)
        error "Invalid argument: $1"
        show_help
        exit 1
        ;;
esac 