#!/usr/bin/env python3
"""
Backend Service Diagnostic Script
Helps identify why the backend service is returning 503 errors.
"""

import requests
import json
import sys
from datetime import datetime

def check_service_status(url: str, service_name: str):
    """Check if a service is responding."""
    print(f"🔍 Checking {service_name}: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 503:
            print(f"   ❌ Service Unavailable - {service_name} is down")
            headers = dict(response.headers)
            if 'x-render-routing' in headers:
                print(f"   🔍 Render Status: {headers['x-render-routing']}")
            return False
        elif response.status_code == 200:
            print(f"   ✅ Service is running")
            try:
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   📊 Response: {response.text[:200]}...")
            return True
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            print(f"   📊 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout - {service_name} is not responding")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error - {service_name} is unreachable")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main diagnostic function."""
    print("🔍 SGE Dashboard Backend Service Diagnostic")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Service URLs
    services = {
        "Backend API Root": "https://sge-dashboard-api.onrender.com/",
        "Backend Health": "https://sge-dashboard-api.onrender.com/health",
        "Backend Grants API": "https://sge-dashboard-api.onrender.com/api/v1/grants",
        "Frontend": "https://sge-dashboard-web.onrender.com/"
    }
    
    results = {}
    
    for service_name, url in services.items():
        print(f"\n{'='*60}")
        results[service_name] = check_service_status(url, service_name)
        print()
    
    # Summary
    print(f"{'='*60}")
    print("📊 DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")
    
    backend_down = not results.get("Backend Health", False)
    frontend_up = results.get("Frontend", False)
    
    if backend_down and frontend_up:
        print("🚨 ISSUE IDENTIFIED: Backend service is down, frontend is up")
        print("\n🔧 REQUIRED ACTIONS:")
        print("1. Check Render backend service logs for errors")
        print("2. Verify DATABASE_URL environment variable is set")
        print("3. Ensure PostgreSQL database is running and accessible")
        print("4. Restart the backend service in Render dashboard")
        print("\n📋 COMMON CAUSES:")
        print("- Database connection failure")
        print("- Missing or incorrect DATABASE_URL")
        print("- Service startup errors")
        print("- Resource limits exceeded")
        
    elif not backend_down and not frontend_up:
        print("🚨 ISSUE: Frontend service is down, backend is up")
        print("\n🔧 REQUIRED ACTIONS:")
        print("1. Check Render frontend service logs")
        print("2. Verify frontend build completed successfully")
        print("3. Restart the frontend service")
        
    elif not backend_down and frontend_up:
        print("✅ SERVICES STATUS: Both frontend and backend are running")
        print("\n🔧 CORS ISSUE:")
        print("- Services are up but CORS might be misconfigured")
        print("- Check CORS_ORIGINS environment variable")
        print("- Verify FRONTEND_URL is set correctly")
        
    else:
        print("🚨 CRITICAL: Both services are down")
        print("\n🔧 REQUIRED ACTIONS:")
        print("1. Check both service logs in Render dashboard")
        print("2. Verify all environment variables are set")
        print("3. Check for any recent deployment issues")
        print("4. Consider rolling back to last working version")
    
    print(f"\n{'='*60}")
    print("🆘 NEXT STEPS:")
    print("1. Go to Render dashboard")
    print("2. Check service logs for detailed error messages")
    print("3. Verify environment variables (especially DATABASE_URL)")
    print("4. Deploy latest commit if needed")
    print("5. Monitor service startup process")
    
    return not backend_down

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 