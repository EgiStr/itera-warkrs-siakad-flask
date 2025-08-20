#!/usr/bin/env python3
"""
WAR KRS Flask Web Application Startup Script
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from app import app, db, init_db
from config_flask import config

def create_app():
    """Create and configure Flask application"""
    # Get configuration from environment
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(config[config_name])
    
    # Create database tables
    with app.app_context():
        init_db()
        print("✅ Database tables created successfully")
    
    return app

def run_development():
    """Run development server"""
    print("🚀 Starting WAR KRS Web Application in Development Mode")
    print("📍 URL: http://localhost:5000")
    print("🔄 Auto-reload enabled")
    print("-" * 50)
    
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

def run_production():
    """Run production server with Gunicorn"""
    print("🚀 Starting WAR KRS Web Application in Production Mode")
    print("⚠️  Make sure to use a proper WSGI server like Gunicorn in production")
    
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False
    )

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'production':
        run_production()
    else:
        run_development()
