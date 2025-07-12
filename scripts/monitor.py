#!/usr/bin/env python3
"""
System Monitor for SGE Dashboard
Simple monitoring script that can be run as a cron job.
"""

import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path

def check_health():
    """Check system health."""
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=10)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, str(e)

def check_cors():
    """Check CORS configuration."""
    try:
        response = requests.get("http://localhost:8000/api/debug/cors", timeout=10)
        if response.status_code == 200:
            config = response.json()
            origins = config.get("cors_origins", [])
            has_production = any("sge-dashboard-web.onrender.com" in origin for origin in origins)
            return has_production, config
        return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_endpoints():
    """Check critical API endpoints."""
    endpoints = [
        "http://localhost:8000/api/v1/grants",
        "http://localhost:8000/api/v1/projects", 
        "http://localhost:8000/api/v1/tasks",
        "http://localhost:8000/api/v1/users"
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            results[endpoint] = {
                "status": response.status_code,
                "success": response.status_code in [200, 307]
            }
        except Exception as e:
            results[endpoint] = {
                "status": "error",
                "success": False,
                "error": str(e)
            }
    
    return results

def log_status(status_data):
    """Log status to file."""
    log_file = Path("logs/monitor.log")
    log_file.parent.mkdir(exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - {json.dumps(status_data)}\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)

def main():
    """Main monitoring function."""
    print(f"🔍 SGE Dashboard Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check health
    health_ok, health_data = check_health()
    print(f"Health: {'✅ OK' if health_ok else '❌ FAILED'}")
    
    # Check CORS
    cors_ok, cors_data = check_cors()
    print(f"CORS: {'✅ OK' if cors_ok else '❌ FAILED'}")
    
    # Check endpoints
    endpoints_data = check_endpoints()
    endpoints_ok = all(result["success"] for result in endpoints_data.values())
    print(f"Endpoints: {'✅ OK' if endpoints_ok else '❌ FAILED'}")
    
    # Overall status
    overall_ok = health_ok and cors_ok and endpoints_ok
    print(f"Overall: {'✅ HEALTHY' if overall_ok else '❌ UNHEALTHY'}")
    
    # Log status
    status_data = {
        "timestamp": datetime.now().isoformat(),
        "health": {"ok": health_ok, "data": health_data},
        "cors": {"ok": cors_ok, "data": cors_data},
        "endpoints": endpoints_data,
        "overall": overall_ok
    }
    
    log_status(status_data)
    
    # Return appropriate exit code
    return 0 if overall_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 