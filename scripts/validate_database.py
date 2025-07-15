#!/usr/bin/env python3
"""
Database Connection Validation Script
Validates DATABASE_URL configuration and tests database connectivity.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def validate_database_url(database_url: str) -> bool:
    """Validate DATABASE_URL format and structure."""
    if not database_url:
        logger.error("DATABASE_URL is empty or not set")
        return False
    
    try:
        parsed = urlparse(database_url)
        
        # Check scheme
        if parsed.scheme not in ['postgresql', 'sqlite']:
            logger.error(f"Unsupported database scheme: {parsed.scheme}")
            return False
        
        # Check for localhost in production
        env = os.getenv('ENV', 'development')
        if env == 'production' and parsed.hostname in ['localhost', '127.0.0.1']:
            logger.error("DATABASE_URL uses localhost in production environment")
            return False
        
        # PostgreSQL specific validation
        if parsed.scheme == 'postgresql':
            if not parsed.hostname:
                logger.error("PostgreSQL DATABASE_URL missing hostname")
                return False
            if not parsed.port:
                logger.warning("PostgreSQL DATABASE_URL missing port (will use default 5432)")
            if not parsed.path or parsed.path == '/':
                logger.error("PostgreSQL DATABASE_URL missing database name")
                return False
        
        logger.info(f"DATABASE_URL format is valid: {parsed.scheme}://{parsed.hostname}:{parsed.port}{parsed.path}")
        return True
        
    except Exception as e:
        logger.error(f"Error parsing DATABASE_URL: {e}")
        return False

def test_database_connection(database_url: str) -> bool:
    """Test actual database connection."""
    try:
        logger.info("Testing database connection...")
        
        # Create engine with minimal configuration
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={"sslmode": "require"} if "render.com" in database_url else {}
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            if test_value == 1:
                logger.info("✅ Database connection successful!")
                return True
            else:
                logger.error(f"❌ Unexpected test query result: {test_value}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "connection refused" in error_str:
            logger.error("   → Database server is not running or not accessible")
            logger.error("   → Check if DATABASE_URL hostname and port are correct")
        elif "authentication failed" in error_str:
            logger.error("   → Database credentials are incorrect")
            logger.error("   → Check username and password in DATABASE_URL")
        elif "database" in error_str and "does not exist" in error_str:
            logger.error("   → Database does not exist")
            logger.error("   → Check database name in DATABASE_URL")
        elif "ssl" in error_str:
            logger.error("   → SSL connection issue")
            logger.error("   → Try adding ?sslmode=require to DATABASE_URL")
        
        return False

def main():
    """Main validation function."""
    logger.info("🔍 SGE Dashboard Database Validation")
    logger.info("=" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=".envV2", override=True)
        logger.info("✅ Loaded environment variables from .envV2")
    except ImportError:
        logger.warning("⚠️  python-dotenv not installed, using system environment only")
    except Exception as e:
        logger.warning(f"⚠️  Could not load .envV2: {e}")
    
    # Get DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable is not set")
        logger.info("\n📋 To fix this:")
        logger.info("1. Set DATABASE_URL in your .envV2 file")
        logger.info("2. For Render: Use the Internal Database URL from your Render dashboard")
        logger.info("3. For local PostgreSQL: postgresql://username:password@localhost:5432/database_name")
        return False
    
    # Mask sensitive information in logs
    masked_url = database_url
    if "@" in masked_url:
        parts = masked_url.split("@")
        if ":" in parts[0]:
            scheme_user = parts[0].split(":")
            if len(scheme_user) >= 3:  # scheme:user:password
                masked_url = f"{scheme_user[0]}:{scheme_user[1]}:***@{parts[1]}"
    
    logger.info(f"🔗 DATABASE_URL: {masked_url}")
    
    # Validate URL format
    if not validate_database_url(database_url):
        logger.error("❌ DATABASE_URL validation failed")
        return False
    
    # Test connection
    if not test_database_connection(database_url):
        logger.error("❌ Database connection test failed")
        return False
    
    logger.info("🎉 All database validation checks passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 