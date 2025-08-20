#!/usr/bin/env python3
"""
Generate encryption key for WAR KRS Flask Application
"""

import secrets
import string
from cryptography.fernet import Fernet

def generate_flask_secret_key():
    """Generate a secure secret key for Flask"""
    # Generate a 32-character random string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def generate_encryption_key():
    """Generate Fernet encryption key"""
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    print("🔐 Generating keys for WAR KRS Flask Application")
    print("=" * 50)
    
    flask_key = generate_flask_secret_key()
    encryption_key = generate_encryption_key()
    
    print("Copy these environment variables to your Vercel project:")
    print()
    print(f"FLASK_SECRET_KEY={flask_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print()
    print("⚠️  Keep these keys secure and never commit them to git!")
    print("   Use Vercel dashboard to set environment variables safely.")
