"""
Vercel API handler for WAR KRS Flask Application
"""

import os
import sys
from pathlib import Path

# Add parent directory and src directory to Python path for imports
parent_path = Path(__file__).parent.parent
src_path = parent_path / 'src'
sys.path.insert(0, str(parent_path))
sys.path.insert(0, str(src_path))

# Set production configuration for Vercel
os.environ.setdefault('FLASK_CONFIG', 'production')

# Import the Flask app
from app import app, db, init_db

# Initialize database on first import (only once)
_db_initialized = False
if not _db_initialized:
    try:
        with app.app_context():
            init_db()
        _db_initialized = True
        print("✅ Database initialized for Vercel")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

# For Vercel serverless functions, we need to export the Flask app directly
# Vercel will handle the WSGI interface automatically
def handler(request):
    """Vercel serverless function handler"""
    with app.app_context():
        return app.full_dispatch_request()

# Export the Flask app for Vercel
# This is what Vercel will use as the WSGI application
app = app
