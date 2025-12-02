"""
Database migration utilities
"""
import os
import logging
from pathlib import Path
from sqlalchemy import text
from app.models.database import engine

logger = logging.getLogger(__name__)


def run_migrations():
    """
    Run database migrations on startup
    Automatically detects database type (SQLite or PostgreSQL) and runs appropriate migrations
    """
    try:
        database_url = os.getenv("DATABASE_URL", "")
        is_postgresql = database_url.startswith("postgresql://") or database_url.startswith("postgres://")
        
        if is_postgresql:
            logger.info("🔧 Detected PostgreSQL database")
            run_postgresql_migrations()
        else:
            logger.info("🔧 Detected SQLite database")
            run_sqlite_migrations()
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        # Don't crash the app, just log the error
        logger.warning("⚠️ Continuing without migrations...")


def run_sqlite_migrations():
    """Run SQLite migrations"""
    migrations = [
        "add_share_token.sql",  # 공유 링크 토큰 (기존)
        "add_enroll_share_fields.sql",  # 친구 초대 필드
        "add_invite_token.sql",  # 초대 링크 토큰
    ]
    
    migrations_dir = Path(__file__).parent.parent.parent / "migrations"
    
    with engine.connect() as conn:
        for migration_file in migrations:
            migration_path = migrations_dir / migration_file
            
            if not migration_path.exists():
                logger.warning(f"⚠️ Migration file not found: {migration_file}")
                continue
            
            try:
                logger.info(f"  Running: {migration_file}")
                
                with open(migration_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Split by semicolon and execute each statement
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                
                for statement in statements:
                    # Skip comments and empty lines
                    if statement.startswith('--') or not statement:
                        continue
                    
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        # Ignore "duplicate column" errors (migration already applied)
                        if "duplicate column" in str(e).lower():
                            logger.debug(f"  Column already exists, skipping...")
                        else:
                            raise
                
                logger.info(f"  ✓ {migration_file} completed")
                
            except Exception as e:
                logger.error(f"  ✗ {migration_file} failed: {e}")
                # Continue with other migrations
                continue
    
    logger.info("✅ SQLite migrations completed")


def run_postgresql_migrations():
    """Run PostgreSQL migrations"""
    migrations = [
        "add_share_token_postgresql.sql",  # 공유 링크 토큰 (기존)
        "add_enroll_share_fields_postgresql.sql",  # 친구 초대 필드
        "add_invite_token_postgresql.sql",  # 초대 링크 토큰
    ]
    
    migrations_dir = Path(__file__).parent.parent.parent / "migrations"
    
    with engine.connect() as conn:
        for migration_file in migrations:
            migration_path = migrations_dir / migration_file
            
            if not migration_path.exists():
                logger.warning(f"⚠️ Migration file not found: {migration_file}")
                continue
            
            try:
                logger.info(f"  Running: {migration_file}")
                
                with open(migration_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Execute the entire migration file
                conn.execute(text(sql_content))
                conn.commit()
                
                logger.info(f"  ✓ {migration_file} completed")
                
            except Exception as e:
                # PostgreSQL migrations use IF NOT EXISTS, so they're safe to re-run
                logger.debug(f"  Migration note: {e}")
                logger.info(f"  ✓ {migration_file} completed (already applied)")
                continue
    
    logger.info("✅ PostgreSQL migrations completed")


def check_migration_status():
    """Check if migrations have been applied"""
    try:
        with engine.connect() as conn:
            # Check if new columns exist
            result = conn.execute(text("SELECT * FROM tombstones LIMIT 0"))
            columns = result.keys()
            
            has_share_token = 'share_token' in columns
            has_enroll = 'enroll' in columns
            has_share = 'share' in columns
            has_invite_token = 'invite_token' in columns
            
            logger.info(f"Migration status:")
            logger.info(f"  - share_token: {'✓' if has_share_token else '✗'}")
            logger.info(f"  - enroll: {'✓' if has_enroll else '✗'}")
            logger.info(f"  - share: {'✓' if has_share else '✗'}")
            logger.info(f"  - invite_token: {'✓' if has_invite_token else '✗'}")
            
            return has_share_token and has_enroll and has_share and has_invite_token
            
    except Exception as e:
        logger.error(f"Failed to check migration status: {e}")
        return False
