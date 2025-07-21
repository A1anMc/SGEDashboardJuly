#!/usr/bin/env python3
"""
Test script to verify deployment fixes
"""

import os
import sys

def test_database_config():
    """Test database configuration."""
    print("\nTesting database configuration...")
    
    # Set up environment for testing
    os.environ["RENDER"] = "true"
    os.environ["ENVIRONMENT"] = "production"
    
    try:
        from app.core.config import settings
        print(f"Environment: {settings.ENV}")
        print(f"Database URL type: {settings.DATABASE_URL.split('://')[0] if settings.DATABASE_URL and '://' in settings.DATABASE_URL else 'not set'}")
        
        from app.db.session import health_check
        health = health_check()
        print(f"Database health: {health}")
        
    except Exception as e:
        print(f"Database config test failed: {e}")

def test_app_import():
    """Test that the app can be imported without errors."""
    print("\nTesting app import...")
    
    try:
        from app.main import app
        print("✓ App imported successfully")
        
        # Test that the health endpoint exists
        routes = [route.path for route in app.routes]
        if "/health" in routes:
            print("✓ Health endpoint found")
        else:
            print("✗ Health endpoint not found")
            print(f"Available routes: {routes}")
            
    except Exception as e:
        print(f"✗ App import failed: {e}")

if __name__ == "__main__":
    print("Testing deployment fixes...")
    test_app_import()
    test_database_config()
    print("\nTest completed!")