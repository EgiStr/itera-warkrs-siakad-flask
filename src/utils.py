"""
Utility functions for WAR KRS application
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


def validate_cookies(cookies: dict) -> bool:
    """
    Validate cookie configuration
    
    Args:
        cookies: Cookie dictionary
        
    Returns:
        True if cookies are valid, False otherwise
    """
    required_cookies = ['ci_session', 'cf_clearance']
    
    for cookie in required_cookies:
        if cookie not in cookies:
            return False
        
        value = cookies[cookie]
        if not value or value.startswith('GANTI_DENGAN'):
            return False
    
    return True


def validate_target_courses(target_courses: dict) -> bool:
    """
    Validate target courses configuration
    
    Args:
        target_courses: Target courses dictionary
        
    Returns:
        True if configuration is valid, False otherwise
    """
    if not target_courses:
        return False
    
    for course_code, class_id in target_courses.items():
        if not course_code or not class_id:
            return False
        
        # Basic format validation
        if '-' not in course_code or not class_id.isdigit():
            return False
    
    return True


def print_banner() -> None:
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                     WAR KRS SIAKAD ITERA                    ║
║                    Automation Tool v1.0                     ║
║                                                              ║
║   🎯 Otomatis mendaftarkan mata kuliah yang diinginkan      ║
║   ⚡ Bruteforce registration sampai berhasil                ║
║   🔒 Aman dengan session management                         ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_configuration_help() -> None:
    """Print help for configuration"""
    help_text = """
📋 CARA KONFIGURASI:

1. Cookie Configuration:
   - Buka browser dan login ke SIAKAD ITERA
   - Tekan F12 → Application → Cookies → https://siakad.itera.ac.id
   - Copy nilai 'ci_session' dan 'cf_clearance'
   - Edit file config/config.json

2. Target Courses:
   - Buka halaman pilih mata kuliah di SIAKAD
   - Inspect element pada dropdown mata kuliah
   - Copy value dari <option value="12345">KODE - NAMA MK</option>
   - Tambahkan ke config.json dengan format:
     "KODE_MK": "ID_KELAS"

3. Settings:
   - delay_seconds: Jeda antar siklus (default: 45 detik)
   - request_timeout: Timeout request (default: 20 detik)

⚠️  PERINGATAN: Jaga kerahasiaan cookie Anda!
"""
    print(help_text)
