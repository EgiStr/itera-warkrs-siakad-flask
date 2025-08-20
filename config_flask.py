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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/warkrs.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': -1,
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
    # Database will be in /tmp (not persistent, consider external DB for production)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/warkrs.db'
    
    # Force HTTPS in production
    PREFERRED_URL_SCHEME = 'https'
    
    # Logging configuration
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
