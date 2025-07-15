#!/usr/bin/env python3
"""
Environment Configuration Checker
Validates that all required environment variables are properly set.
"""

import os
import sys
import re
from urllib.parse import urlparse

def check_required_env_vars():
    """Check that all required environment variables are set."""
    print("🔍 Environment Variables Check")
    print("=" * 50)
    
    required_vars = {
        'DATABASE_URL': 'Database connection string',
        'SECRET_KEY': 'Application secret key',
        'JWT_SECRET_KEY': 'JWT signing key',
        'ENVIRONMENT': 'Environment (production/development)',
    }
    
    optional_vars = {
        'FRONTEND_URL': 'Frontend URL for CORS',
        'CORS_ORIGINS': 'Allowed CORS origins',
        # Removed Supabase references
        'SENTRY_DSN': 'Error tracking DSN',
    }
    
    issues = []
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ {var}: Missing ({description})")
            issues.append(f"{var} is required")
        else:
            # Validate specific formats
            if var == 'DATABASE_URL':
                if not value.startswith(('postgresql://', 'sqlite:///')):
                    print(f"❌ {var}: Invalid format (must start with postgresql:// or sqlite:///)")
                    issues.append(f"{var} has invalid format")
                else:
                    print(f"✅ {var}: Set")
            elif var in ['SECRET_KEY', 'JWT_SECRET_KEY']:
                if len(value) < 32:
                    print(f"❌ {var}: Too short (minimum 32 characters)")
                    issues.append(f"{var} is too short")
                else:
                    print(f"✅ {var}: Set (length: {len(value)})")
            else:
                print(f"✅ {var}: Set")
    
    # Check optional variables
    print(f"\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️  {var}: Not set ({description})")
    
    return len(issues) == 0, issues

def check_production_readiness():
    """Check if configuration is production-ready."""
    print(f"\n🔍 Production Readiness Check")
    print("-" * 30)
    
    issues = []
    
    # Check environment
    env = os.getenv('ENVIRONMENT', 'development')
    if env != 'production':
        print(f"⚠️  ENVIRONMENT: {env} (should be 'production' for deployment)")
    else:
        print(f"✅ ENVIRONMENT: {env}")
    
    # Check debug mode
    debug = os.getenv('DEBUG', 'false').lower()
    if debug == 'true' and env == 'production':
        print("❌ DEBUG: Enabled in production (security risk)")
        issues.append("DEBUG mode enabled in production")
    else:
        print(f"✅ DEBUG: {debug}")
    
    # Check secret keys
    secret_key = os.getenv('SECRET_KEY', '')
    if secret_key in ['your-secret-key-change-in-production', 'development-secret-key']:
        print("❌ SECRET_KEY: Using default/development key")
        issues.append("SECRET_KEY is not production-ready")
    elif len(secret_key) >= 32:
        print("✅ SECRET_KEY: Production-ready")
    
    # Check CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', '')
    if '*' in cors_origins and env == 'production':
        print("❌ CORS_ORIGINS: Wildcard (*) not recommended for production")
        issues.append("CORS allows all origins")
    elif cors_origins:
        print("✅ CORS_ORIGINS: Configured")
    
    return len(issues) == 0, issues

def main():
    """Run environment checks."""
    print("🔍 SGE Dashboard Environment Check")
    print("=" * 60)
    
    # Check required variables
    env_ok, env_issues = check_required_env_vars()
    
    # Check production readiness
    prod_ok, prod_issues = check_production_readiness()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 ENVIRONMENT CHECK SUMMARY")
    print(f"{'='*60}")
    
    all_issues = env_issues + prod_issues
    
    if not all_issues:
        print("🎉 Environment configuration is ready for production!")
        return True
    else:
        print(f"❌ Found {len(all_issues)} issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 Recommended actions:")
        print("1. Set missing environment variables in Render dashboard")
        print("2. Generate secure secret keys (32+ characters)")
        print("3. Configure CORS origins properly")
        print("4. Set ENVIRONMENT=production for deployment")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 