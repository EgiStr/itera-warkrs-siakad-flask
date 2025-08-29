"""
Database migration helper for production deployment
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from app import app, db, User, UserSettings, Course, WarSession, ActivityLog
from config_flask import config

def init_production_db():
    """Initialize database for production deployment"""
    
    # Set production config
    os.environ['FLASK_CONFIG'] = 'production'
    app.config.from_object(config['production'])
    
    print("🗄️  Initializing production database...")
    print(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    with app.app_context():
        try:
            # First, fix database schema
            print("🔧 Fixing database schema...")
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
                    print(f"✅ Schema fix: {query}")
                except Exception as e:
                    print(f"⚠️  Schema fix (might be OK): {e}")
            
            db.session.commit()
            print("✅ Database schema fixed")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if we can connect and query
            user_count = User.query.count()
            course_count = Course.query.count()
            
            print(f"📊 Current data:")
            print(f"   Users: {user_count}")
            print(f"   Courses: {course_count}")
            
            # Try to migrate courses if none exist
            if course_count == 0:
                print("📚 No courses found, attempting migration...")
                # Use no_autoflush to prevent premature flush
                with db.session.no_autoflush:
                    from app import migrate_courses_from_md
                    migrate_courses_from_md()
                
                course_count = Course.query.count()
                print(f"✅ Migrated {course_count} courses")
            
            print("✅ Production database initialization completed")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_production_db()
