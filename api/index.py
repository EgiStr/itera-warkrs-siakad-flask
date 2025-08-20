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

# Import the Flask app with error handling
try:
    from app import app as flask_app, db, init_db
    
    # Initialize database on import
    with flask_app.app_context():
        try:
            init_db()
            print("✅ Database initialized for Vercel")
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
            
    # Export for Vercel
    app = flask_app
    
except Exception as e:
    print(f"❌ Error importing Flask app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create minimal error app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/<path:path>')
    def error_handler(path=None):
        return {
            'error': 'Application failed to initialize',
            'details': str(e),
            'path': path or '/'
        }, 500
