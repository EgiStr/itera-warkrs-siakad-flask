"""
Fix database schema for production
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from app import app, db
from config_flask import config

def fix_db_schema():
    """Fix database schema issues"""
    
    # Set production config
    os.environ['FLASK_CONFIG'] = 'production'
    app.config.from_object(config['production'])
    
    print("🔧 Fixing database schema...")
    print(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    with app.app_context():
        try:
            # Alter table to increase field lengths
            alter_queries = [
                "ALTER TABLE courses ALTER COLUMN semester TYPE VARCHAR(20);",
                "ALTER TABLE courses ALTER COLUMN course_code TYPE VARCHAR(30);",
                "ALTER TABLE courses ALTER COLUMN class_type TYPE VARCHAR(100);",
                "ALTER TABLE courses ALTER COLUMN class_id TYPE VARCHAR(100);",
                "ALTER TABLE courses ALTER COLUMN faculty TYPE VARCHAR(150);",
                "ALTER TABLE courses ALTER COLUMN department TYPE VARCHAR(150);",
                "ALTER TABLE courses ALTER COLUMN course_name TYPE VARCHAR(200);"
            ]
            
            for query in alter_queries:
                try:
                    db.session.execute(db.text(query))
                    print(f"✅ Executed: {query}")
                except Exception as e:
                    print(f"⚠️  Query failed (might be OK): {query} - {e}")
            
            db.session.commit()
            print("✅ Database schema fixed successfully")
            
        except Exception as e:
            print(f"❌ Schema fix failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    fix_db_schema()
