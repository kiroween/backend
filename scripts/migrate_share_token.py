#!/usr/bin/env python3
"""
Add share_token column to tombstones table
"""
import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import env_config


def migrate():
    """Run migration to add share_token column"""
    db_path = env_config.database_url.replace("sqlite:///", "")
    
    print(f"📦 Connecting to database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(tombstones)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "share_token" in columns:
            print("✅ share_token column already exists. Skipping migration.")
            return
        
        print("🔧 Adding share_token column...")
        
        # Add share_token column
        cursor.execute("ALTER TABLE tombstones ADD COLUMN share_token VARCHAR(100)")
        
        # Create unique index
        cursor.execute("CREATE UNIQUE INDEX idx_tombstones_share_token ON tombstones(share_token)")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
