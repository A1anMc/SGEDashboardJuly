#!/usr/bin/env python3
"""
Full System Health Check
Comprehensive check of all system components.
"""

import requests
import os
import sys
import json
from datetime import datetime

def check_backend_health():
    """Check backend service health."""
    print("\n🔍 Backend Health Check")
    print("-" * 30)
    
    # Detect environment - check for local development first
    backend_urls = [
        "http://localhost:8000/api/v1/health",  # Local development
        "https://sge-dashboard-api.onrender.com/health"  # Production
    ]
    
    for url in backend_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Backend: Healthy")
                print(f"   URL: {url}")
                print(f"   Status: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Backend: Status {response.status_code}")
                return False
        except Exception as e:
            if "localhost" in url:
                continue  # Try production URL
            print(f"❌ Backend: {e}")
            return False
    
    print("❌ Backend: No accessible backend found")
    return False

def check_frontend_health():
    """Check frontend service health."""
    print("\n🔍 Frontend Health Check")
    print("-" * 30)
    
    try:
        response = requests.get("https://sge-dashboard-web.onrender.com", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: Healthy")
            return True
        else:
            print(f"❌ Frontend: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend: {e}")
        return False

def check_api_endpoints():
    """Check critical API endpoints."""
    print("\n🔍 API Endpoints Check")
    print("-" * 30)
    
    endpoints = [
        "/api/v1/grants",
        "/api/v1/projects", 
        "/api/v1/tasks",
        "/api/v1/users"
    ]
    
    # Detect environment - check for local development first
    base_urls = [
        "http://localhost:8000",  # Local development
        "https://sge-dashboard-api.onrender.com"  # Production
    ]
    
    base_url = None
    for url in base_urls:
        try:
            response = requests.get(f"{url}/api/v1/health", timeout=3)
            if response.status_code == 200:
                base_url = url
                break
        except:
            continue
    
    if not base_url:
        print("❌ No accessible backend found")
        return False
    
    working = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code in [200, 401, 422]:  # 401/422 are OK (auth required)
                print(f"✅ {endpoint}: Status {response.status_code}")
                working += 1
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    return working == len(endpoints)

def check_cors():
    """Check CORS configuration."""
    print("\n🔍 CORS Check")
    print("-" * 30)
    
    # Detect environment - check for local development first
    base_urls = [
        "http://localhost:8000",  # Local development
        "https://sge-dashboard-api.onrender.com"  # Production
    ]
    
    origins = [
        "http://localhost:3000",  # Local development
        "https://sge-dashboard-web.onrender.com"  # Production
    ]
    
    for base_url, origin in zip(base_urls, origins):
        try:
            # First check if backend is accessible
            health_response = requests.get(f"{base_url}/api/v1/health", timeout=3)
            if health_response.status_code != 200:
                continue
                
            headers = {
                'Origin': origin,
                'Access-Control-Request-Method': 'GET'
            }
            
            response = requests.options(
                f"{base_url}/api/v1/grants",
                headers=headers,
                timeout=5
            )
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            if cors_origin:
                print(f"✅ CORS: Configured ({cors_origin})")
                return True
            else:
                print("❌ CORS: Not configured")
                return False
                
        except Exception as e:
            if "localhost" in base_url:
                continue  # Try production
            print(f"❌ CORS: {e}")
            return False
    
    print("❌ CORS: No accessible backend found")
    return False

def main():
    """Run full system check."""
    print("🔍 SGE Dashboard Full System Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    checks = [
        ("Backend", check_backend_health),
        ("Frontend", check_frontend_health), 
        ("API Endpoints", check_api_endpoints),
        ("CORS", check_cors)
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    # Summary
    print("\n" + "="*50)
    print("📊 SYSTEM STATUS SUMMARY")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}: {'PASS' if status else 'FAIL'}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 System is fully operational!")
    elif passed >= total // 2:
        print("⚠️  System partially operational - some issues need attention")
    else:
        print("🚨 System has critical issues - immediate attention required")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 