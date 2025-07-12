#!/usr/bin/env python3
"""
Database Schema Checker
Verifies that database tables exist and migrations are applied.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def check_database_schema():
    """Check if database schema is properly set up."""
    print("🔍 Checking Database Schema")
    print("=" * 50)
    
    # Expected tables based on your models
    expected_tables = [
        'user', 'project', 'task', 'grants', 'tags', 
        'task_comment', 'time_entry', 'team_member',
        'alembic_version'  # Migration tracking table
    ]
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        # Create engine and check connection
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        # Get existing tables
        existing_tables = inspector.get_table_names()
        print(f"📊 Found {len(existing_tables)} tables in database")
        
        # Check for missing tables
        missing_tables = set(expected_tables) - set(existing_tables)
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            print("🔧 Run: alembic upgrade head")
            return False
        
        print("✅ All expected tables exist")
        
        # Check alembic version
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                print(f"📋 Database migration version: {version}")
        except:
            print("⚠️  Could not check migration version")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    success = check_database_schema()
    sys.exit(0 if success else 1) 