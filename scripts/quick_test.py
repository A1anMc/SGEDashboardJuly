#!/usr/bin/env python3
"""
Quick Test Script for SGE Dashboard
Runs essential tests to catch issues fast.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(command, timeout=30):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd()
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_backend_startup():
    """Test backend startup."""
    print("🔍 Testing backend startup...")
    success, stdout, stderr = run_command(
        'python -c "from app.main import create_app; app = create_app(); print(\'Backend startup OK\')"'
    )
    if success:
        print("✅ Backend startup: PASSED")
        return True
    else:
        print("❌ Backend startup: FAILED")
        print(f"Error: {stderr}")
        return False

def test_database_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    success, stdout, stderr = run_command(
        'python -c "from app.db.session import get_db_session; next(get_db_session()); print(\'Database connection OK\')"'
    )
    if success:
        print("✅ Database connection: PASSED")
        return True
    else:
        print("❌ Database connection: FAILED")
        print(f"Error: {stderr}")
        return False

def test_api_health():
    """Test API health endpoint."""
    print("🔍 Testing API health...")
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ API health: PASSED")
            return True
        else:
            print(f"❌ API health: FAILED (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API health: FAILED ({str(e)})")
        return False

def test_cors_config():
    """Test CORS configuration."""
    print("🔍 Testing CORS configuration...")
    try:
        response = requests.get("http://localhost:8000/api/debug/cors", timeout=5)
        if response.status_code == 200:
            config = response.json()
            origins = config.get("cors_origins", [])
            has_production = any("sge-dashboard-web.onrender.com" in origin for origin in origins)
            if has_production:
                print("✅ CORS configuration: PASSED")
                return True
            else:
                print("❌ CORS configuration: FAILED (missing production domains)")
                return False
        else:
            print(f"❌ CORS configuration: FAILED (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ CORS configuration: FAILED ({str(e)})")
        return False

def test_critical_imports():
    """Test critical imports."""
    print("🔍 Testing critical imports...")
    critical_imports = [
        "from app.core.config import settings",
        "from app.db.session import get_db_session",
        "from app.models.grant import Grant",
        "from app.api.v1.api import api_router",
        "from app.services.scrapers.australian_grants_scraper import AustralianGrantsScraper"
    ]
    
    for import_statement in critical_imports:
        success, stdout, stderr = run_command(f'python -c "{import_statement}; print(\'OK\')"')
        if not success:
            print(f"❌ Import failed: {import_statement}")
            print(f"Error: {stderr}")
            return False
    
    print("✅ Critical imports: PASSED")
    return True

def main():
    """Run quick tests."""
    print("🚀 SGE Dashboard Quick Test Suite")
    print("=" * 50)
    
    tests = [
        test_critical_imports,
        test_backend_startup,
        test_database_connection,
        test_api_health,
        test_cors_config,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 