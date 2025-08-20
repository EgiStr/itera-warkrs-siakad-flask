"""
Flask Configuration for WAR KRS Web Application
"""

import os
from pathlib import Path

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'war-krs-secret-key-change-in-production'
    
    # Database configuration
    BASE_DIR = Path(__file__).parent
    database_url = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/warkrs.db'
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Engine options based on database type
    if database_url and database_url.startswith('postgresql://'):
        # PostgreSQL-specific options
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_timeout': 20,
            'pool_recycle': -1,
            'pool_pre_ping': True,
            'pool_size': 5,
            'max_overflow': 10
        }
    else:
        # SQLite-specific options (no pool options)
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True
        }
    
    # Flask-Login configuration
    REMEMBER_COOKIE_DURATION = 86400  # 24 hours
    
    # WTF configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Security headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files
    
    # Encryption key for SIAKAD passwords
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # WAR KRS specific settings
    MAX_WAR_SESSIONS_PER_USER = 1
    DEFAULT_CYCLE_DELAY = 5  # seconds
    DEFAULT_REQUEST_TIMEOUT = 20  # seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Vercel-specific configuration
    # For serverless functions, we'll use SQLite in /tmp
    # Override DATABASE_URL if it's PostgreSQL and we're on Vercel
    database_url = os.environ.get('DATABASE_URL', 'sqlite:////tmp/warkrs.db')
    if database_url and database_url.startswith('postgres://'):
        # Force SQLite for Vercel serverless functions
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/warkrs.db'
    else:
        SQLALCHEMY_DATABASE_URI = database_url
    
    # Force HTTPS in production
    PREFERRED_URL_SCHEME = 'https'
    
    # Logging configuration
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # Use PostgreSQL if available, otherwise fall back to in-memory SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgresql://'):
        SQLALCHEMY_DATABASE_URI = database_url
        # PostgreSQL-specific options for testing
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_timeout': 20,
            'pool_recycle': -1,
            'pool_pre_ping': True,
            'pool_size': 2,  # Smaller pool for testing
            'max_overflow': 5
        }
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        # SQLite-specific options
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True
        }
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
