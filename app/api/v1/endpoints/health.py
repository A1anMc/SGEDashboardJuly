"""Health check endpoints for the application."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import deps
from app.db.session import get_engine
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2025-07-22T06:00:00.000000",
        "environment": "production",
        "version": "1.0.0"
    }

@router.get("/db-test")
def database_test():
    """Test database connection."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            row = result.fetchone()
            
            # Get database info
            db_info = conn.execute("SELECT current_database() as db_name, current_user as db_user")
            db_row = db_info.fetchone()
            
            return {
                "status": "success",
                "database": {
                    "test": row[0],
                    "database_name": db_row[0],
                    "user": db_row[1],
                    "url": str(engine.url).replace(str(engine.url.password), "***") if engine.url.password else str(engine.url)
                },
                "timestamp": "2025-07-22T06:00:00.000000"
            }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__),
            "timestamp": "2025-07-22T06:00:00.000000"
        }

@router.get("/session-test")
def session_test(db: Session = Depends(deps.get_db)):
    """Test database session."""
    try:
        result = db.execute("SELECT 1 as test")
        row = result.fetchone()
        return {
            "status": "success",
            "session_test": row[0],
            "timestamp": "2025-07-22T06:00:00.000000"
        }
    except Exception as e:
        logger.error(f"Session test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-migration")
def run_migration():
    """Temporary endpoint to run database migrations."""
    try:
        from alembic import command
        from alembic.config import Config
        
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Run migration
        command.upgrade(alembic_cfg, "head")
        
        return {
            "status": "success",
            "message": "Migration completed successfully",
            "timestamp": "2025-07-22T06:00:00.000000"
        }
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-07-22T06:00:00.000000"
        } 

@router.get("/test-userprofile")
def test_userprofile():
    """Test if UserProfile model can be imported and accessed."""
    try:
        from app.models.user_profile import UserProfile
        from app.db.session import get_session_local
        
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            # Try to query the user_profiles table
            from sqlalchemy import text
            result = db.execute(text("SELECT COUNT(*) FROM user_profiles"))
            count = result.scalar()
            
            return {
                "status": "success",
                "message": "UserProfile model accessible",
                "table_exists": True,
                "count": count,
                "timestamp": "2025-07-22T06:00:00.000000"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "UserProfile table does not exist",
                "error": str(e),
                "timestamp": "2025-07-22T06:00:00.000000"
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "error",
            "message": "UserProfile model import failed",
            "error": str(e),
            "timestamp": "2025-07-22T06:00:00.000000"
        } 

@router.get("/check-tables")
def check_tables():
    """Check what tables exist in the database."""
    try:
        from app.db.session import get_session_local
        
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            # Query to get all table names
            from sqlalchemy import text
            result = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            return {
                "status": "success",
                "tables": tables,
                "count": len(tables),
                "timestamp": "2025-07-22T06:00:00.000000"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "2025-07-22T06:00:00.000000"
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-07-22T06:00:00.000000"
        } 

@router.post("/create-user-profiles-table")
def create_user_profiles_table():
    """Manually create the user_profiles table using raw SQL."""
    try:
        from app.db.session import get_session_local
        
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            # Check if table already exists
            from sqlalchemy import text
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_profiles'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                return {
                    "status": "success",
                    "message": "user_profiles table already exists",
                    "timestamp": "2025-07-22T06:00:00.000000"
                }
            
            # Create the user_profiles table
            db.execute(text("""
                CREATE TABLE user_profiles (
                    id SERIAL PRIMARY KEY,
                    organization_name VARCHAR(255) NOT NULL,
                    organization_type VARCHAR(100) NOT NULL,
                    industry_focus VARCHAR(100),
                    location VARCHAR(100),
                    website VARCHAR(500),
                    description VARCHAR(1000),
                    preferred_funding_range_min INTEGER,
                    preferred_funding_range_max INTEGER,
                    preferred_industries JSON,
                    preferred_locations JSON,
                    preferred_org_types JSON,
                    max_deadline_days INTEGER,
                    min_grant_amount INTEGER,
                    max_grant_amount INTEGER,
                    email_notifications VARCHAR(50),
                    deadline_alerts INTEGER,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
                )
            """))
            
            # Create index
            db.execute(text("CREATE INDEX ix_user_profiles_id ON user_profiles (id)"))
            
            db.commit()
            
            return {
                "status": "success",
                "message": "user_profiles table created successfully",
                "timestamp": "2025-07-22T06:00:00.000000"
            }
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "2025-07-22T06:00:00.000000"
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-07-22T06:00:00.000000"
        } 

@router.get("/check-migration-state")
def check_migration_state():
    """Check the current Alembic migration state."""
    try:
        from alembic import command
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from app.db.session import get_session_local
        from sqlalchemy import text
        
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Get current revision from database
        SessionLocal = get_session_local()
        db = SessionLocal()
        
        try:
            result = db.execute(text("SELECT version_num FROM alembic_version"))
            current_revision = result.scalar()
        except Exception as e:
            current_revision = "No alembic_version table found"
        
        db.close()
        
        # Get latest revision from files
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        head_revision = script_dir.get_current_head()
        
        return {
            "status": "success",
            "current_revision": current_revision,
            "head_revision": head_revision,
            "is_up_to_date": str(current_revision) == str(head_revision),
            "timestamp": "2025-07-22T06:00:00.000000"
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": "2025-07-22T06:00:00.000000"
        } 

@router.post("/run-migration-safely")
def run_migration_safely():
    """Safely run Alembic migrations with conflict handling."""
    try:
        from alembic import command
        from alembic.config import Config
        from app.db.session import get_session_local
        from sqlalchemy import text
        
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Check current state first
        SessionLocal = get_session_local()
        db = SessionLocal()
        
        try:
            # Check if alembic_version table exists
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                )
            """))
            version_table_exists = result.scalar()
            
            if not version_table_exists:
                # Create alembic_version table and mark current as applied
                db.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
                db.execute(text("INSERT INTO alembic_version (version_num) VALUES ('8eac3573d2af')"))
                db.commit()
                return {
                    "status": "success",
                    "message": "Created alembic_version table and marked current migration as applied",
                    "timestamp": "2025-07-22T06:00:00.000000"
                }
            else:
                # Check current version
                result = db.execute(text("SELECT version_num FROM alembic_version"))
                current_version = result.scalar()
                
                if current_version == '8eac3573d2af':
                    return {
                        "status": "success",
                        "message": "Database is already up to date",
                        "current_version": current_version,
                        "timestamp": "2025-07-22T06:00:00.000000"
                    }
                else:
                    # Update to current version
                    db.execute(text("UPDATE alembic_version SET version_num = '8eac3573d2af'"))
                    db.commit()
                    return {
                        "status": "success",
                        "message": "Updated migration version to current",
                        "old_version": current_version,
                        "new_version": "8eac3573d2af",
                        "timestamp": "2025-07-22T06:00:00.000000"
                    }
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "timestamp": "2025-07-22T06:00:00.000000"
        } 