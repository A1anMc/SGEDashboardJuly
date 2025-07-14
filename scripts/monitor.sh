#!/bin/bash

# Monitor script wrapper for SGE Dashboard
# This script provides a convenient way to run the monitoring system

# Default values
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
INTERVAL=${INTERVAL:-60}
LOG_DIR="logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Help function
show_help() {
    echo "SGE Dashboard Monitoring Script"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -u, --url URL        Backend URL to monitor (default: $BACKEND_URL)"
    echo "  -i, --interval SEC   Check interval in seconds (default: $INTERVAL)"
    echo "  -o, --once           Run checks once and exit"
    echo "  -f, --follow         Follow log output in real-time"
    echo
    echo "Environment variables:"
    echo "  BACKEND_URL    Alternative way to set backend URL"
    echo "  INTERVAL       Alternative way to set check interval"
}

# Parse command line arguments
FOLLOW=0
ONCE=0
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--url)
            BACKEND_URL="$2"
            shift 2
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -o|--once)
            ONCE=1
            shift
            ;;
        -f|--follow)
            FOLLOW=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Function to check Python dependencies
check_dependencies() {
    echo "Checking Python dependencies..."
    pip install -q psutil requests
}

# Function to run the monitor
run_monitor() {
    local args=()
    
    [[ -n "$BACKEND_URL" ]] && args+=(--backend-url "$BACKEND_URL")
    [[ -n "$INTERVAL" ]] && args+=(--interval "$INTERVAL")
    [[ $ONCE -eq 1 ]] && args+=(--once)
    
    python3 "$(dirname "$0")/monitor.py" "${args[@]}"
}

# Main execution
check_dependencies

if [[ $FOLLOW -eq 1 ]]; then
    # Run monitor in background and follow logs
    run_monitor &
    tail -f "$LOG_DIR/monitor.json"
else
    # Run monitor normally
    run_monitor
fi 