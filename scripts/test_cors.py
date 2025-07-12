#!/usr/bin/env python3
"""
CORS and API Connectivity Test Script
Tests the connection between frontend and backend with CORS headers.
"""

import requests
import json
import sys
from urllib.parse import urljoin

def test_cors_preflight(api_url: str, frontend_url: str):
    """Test CORS preflight request."""
    print(f"🔍 Testing CORS preflight from {frontend_url} to {api_url}")
    
    headers = {
        'Origin': frontend_url,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
    }
    
    try:
        response = requests.options(api_url, headers=headers, timeout=10)
        print(f"✅ Preflight Status: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print("📋 CORS Headers:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Preflight failed: {e}")
        return False

def test_api_endpoint(api_url: str, frontend_url: str):
    """Test actual API endpoint."""
    print(f"\n🔍 Testing API endpoint: {api_url}")
    
    headers = {
        'Origin': frontend_url,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        print(f"✅ API Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📊 Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"📊 Response: {response.text[:200]}...")
        else:
            print(f"❌ Error Response: {response.text[:200]}...")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ API request failed: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 SGE Dashboard CORS & API Connectivity Test")
    print("=" * 60)
    
    # URLs from the screenshot
    frontend_url = "https://sge-dashboard-web.onrender.com"
    backend_base = "https://sge-dashboard-api.onrender.com"
    
    # Test endpoints
    endpoints = [
        "/health",
        "/api/v1/grants/status=open&page=1&size=10",
        "/api/v1/grants",
        "/"
    ]
    
    all_passed = True
    
    for endpoint in endpoints:
        api_url = urljoin(backend_base, endpoint)
        print(f"\n{'='*60}")
        print(f"Testing: {endpoint}")
        print(f"{'='*60}")
        
        # Test CORS preflight
        preflight_ok = test_cors_preflight(api_url, frontend_url)
        
        # Test actual API call
        api_ok = test_api_endpoint(api_url, frontend_url)
        
        if not (preflight_ok and api_ok):
            all_passed = False
            print(f"❌ {endpoint} - FAILED")
        else:
            print(f"✅ {endpoint} - PASSED")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 All tests passed! CORS is properly configured.")
    else:
        print("❌ Some tests failed. Check CORS configuration.")
        print("\n🔧 Possible fixes:")
        print("1. Ensure FRONTEND_URL is set correctly in backend environment")
        print("2. Check CORS_ORIGINS includes the frontend URL")
        print("3. Verify backend is running and accessible")
        print("4. Check for any firewall or network issues")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 