#!/bin/bash

# NavImpact Baseline Protection Script
# Ensures safe development practices and baseline protection

set -e

echo "🛡️ NavImpact Baseline Protection"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASELINE_TAG="v1.0.0-baseline"

# Function to check if we're on main branch
check_main_branch() {
    if [[ $(git branch --show-current) == "main" ]]; then
        echo -e "${RED}⚠️  WARNING: You're on the main branch!${NC}"
        echo -e "${YELLOW}   For development, create a feature branch:${NC}"
        echo -e "${BLUE}   git checkout $BASELINE_TAG${NC}"
        echo -e "${BLUE}   git checkout -b feature/your-feature-name${NC}"
        echo ""
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to verify baseline integrity
verify_baseline() {
    echo -e "${BLUE}🔍 Verifying baseline integrity...${NC}"
    
    # Check if baseline tag exists
    if ! git tag -l | grep -q "$BASELINE_TAG"; then
        echo -e "${RED}❌ Baseline tag $BASELINE_TAG not found!${NC}"
        exit 1
    fi
    
    # Check if baseline is accessible
    if ! git show "$BASELINE_TAG" > /dev/null 2>&1; then
        echo -e "${RED}❌ Cannot access baseline tag!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Baseline tag verified${NC}"
}

# Function to check for uncommitted changes
check_uncommitted() {
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}⚠️  You have uncommitted changes!${NC}"
        echo -e "${BLUE}   Consider committing or stashing them first.${NC}"
        echo ""
        git status --short
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to create safe feature branch
create_feature_branch() {
    echo -e "${BLUE}🌿 Creating feature branch from baseline...${NC}"
    
    # Ensure we're starting from baseline
    git checkout "$BASELINE_TAG"
    
    # Get feature name from user
    read -p "Enter feature name (e.g., 'add-user-auth'): " feature_name
    
    if [[ -z "$feature_name" ]]; then
        echo -e "${RED}❌ Feature name cannot be empty${NC}"
        exit 1
    fi
    
    # Create and switch to feature branch
    git checkout -b "feature/$feature_name"
    
    echo -e "${GREEN}✅ Created feature branch: feature/$feature_name${NC}"
    echo -e "${BLUE}   You can now safely develop your feature!${NC}"
}

# Function to run baseline verification
run_verification() {
    echo -e "${BLUE}🧪 Running baseline verification...${NC}"
    
    if [[ -f "./scripts/verify-baseline.sh" ]]; then
        ./scripts/verify-baseline.sh
    else
        echo -e "${YELLOW}⚠️  Verification script not found${NC}"
        echo -e "${BLUE}   Running basic health check...${NC}"
        curl -s https://navimpact-api.onrender.com/health | python3 -m json.tool
    fi
}

# Function to show current status
show_status() {
    echo -e "${BLUE}📊 Current Status:${NC}"
    echo "  • Branch: $(git branch --show-current)"
    echo "  • Commit: $(git rev-parse --short HEAD)"
    echo "  • Baseline: $BASELINE_TAG"
    echo "  • Uncommitted changes: $(if git diff-index --quiet HEAD --; then echo "None"; else echo "Yes"; fi)"
    echo ""
}

# Function to show rollback commands
show_rollback() {
    echo -e "${BLUE}🚨 Emergency Rollback Commands:${NC}"
    echo "  • Rollback to baseline: git reset --hard $BASELINE_TAG"
    echo "  • Force push: git push --force origin main"
    echo "  • Verify: ./scripts/verify-baseline.sh"
    echo ""
}

# Main menu
show_menu() {
    echo "Choose an action:"
    echo "  1) Create feature branch from baseline"
    echo "  2) Verify baseline integrity"
    echo "  3) Run baseline verification tests"
    echo "  4) Show current status"
    echo "  5) Show rollback commands"
    echo "  6) Exit"
    echo ""
}

# Main execution
main() {
    verify_baseline
    check_main_branch
    check_uncommitted
    show_status
    
    while true; do
        show_menu
        read -p "Enter choice (1-6): " choice
        
        case $choice in
            1)
                create_feature_branch
                break
                ;;
            2)
                verify_baseline
                echo -e "${GREEN}✅ Baseline integrity verified!${NC}"
                ;;
            3)
                run_verification
                ;;
            4)
                show_status
                ;;
            5)
                show_rollback
                ;;
            6)
                echo -e "${GREEN}👋 Stay safe and protect your baseline!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid choice${NC}"
                ;;
        esac
        
        echo ""
    done
}

# Run main function
main 