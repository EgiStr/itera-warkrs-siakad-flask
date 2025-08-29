"""
Flask Web Application for WAR KRS
Implementation based on PRD requirements for simple Flask web app
"""

import os
import sys
import json
import threading
import time
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Flask core imports
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Form handling imports
try:
    from flask_wtf import FlaskForm
    from wtforms import StringField, PasswordField, SelectMultipleField, TextAreaField, SubmitField
    from wtforms.validators import DataRequired, Length, ValidationError
except ImportError as e:
    print(f"❌ Flask-WTF import error: {e}")
    print("Please install compatible versions: pip install -r requirements-flask.txt")
    sys.exit(1)

# Security imports
try:
    from cryptography.fernet import Fernet
except ImportError as e:
    print(f"❌ Cryptography import error: {e}")
    print("Please install: pip install cryptography==41.0.7")
    sys.exit(1)

# Import existing business logic (with error handling)
try:
    from src.controller import WARKRSController
    from src.telegram_notifier import TelegramNotifier
    CONTROLLER_AVAILABLE = True
    print("✅ Existing WAR controller imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import existing business logic: {e}")
    print("    Using fallback WAR implementation.")
    CONTROLLER_AVAILABLE = False

# Import Celery for background tasks (with error handling)
try:
    from celery_app import celery_app
    from tasks.war_tasks import run_war_task, stop_war_task
    CELERY_AVAILABLE = True
    print("✅ Celery task system imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import Celery: {e}")
    print("    Falling back to threading approach.")
    CELERY_AVAILABLE = False
    
    # Create dummy classes to prevent crashes
    class WARKRSController:
        def __init__(self, cookies=None, urls=None, target_courses=None, settings=None, telegram_config=None, debug_mode=False):
            self.cookies = cookies or {}
            self.urls = urls or {}
            self.target_courses = target_courses or {}
            self.settings = settings or {}
            self.telegram_config = telegram_config
            self.debug_mode = debug_mode
            
            # Initialize remaining targets from target_courses
            self.remaining_targets = set(target_courses.keys()) if target_courses else set()
            self.cycle_count = 0
            
            print(f"🔄 Fallback controller initialized with {len(self.remaining_targets)} target courses")
        
        def run_single_cycle(self):
            """Simplified single cycle implementation"""
            self.cycle_count += 1
            print(f"🔄 Running fallback cycle {self.cycle_count}")
            
            # Simulate some processing
            import time
            time.sleep(2)
            
            # For demo purposes, randomly succeed or fail
            import random
            if random.random() < 0.3:  # 30% chance of success
                # Pick a random course to "succeed"
                if self.remaining_targets:
                    successful = [list(self.remaining_targets)[0]]
                    self.remaining_targets.discard(successful[0])
                    return True, {'status': 'ok'}, successful, []
            
            # Otherwise, all failed
            failed = list(self.remaining_targets)
            return True, {'status': 'ok'}, [], failed
    
    class TelegramNotifier:
        def __init__(self, *args, **kwargs):
            pass
        
        def send_message(self, *args, **kwargs):
            pass
            return False, {}, [], []

# Initialize Flask app with static file configuration
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Load configuration (with error handling)
try:
    from config_flask import config
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(config[config_name])
except ImportError:
    # Fallback configuration if config_flask.py is missing
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///warkrs.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    print("⚠️  Using fallback configuration. Create config_flask.py for proper setup.")

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

# Add custom Jinja2 filters
@app.template_filter('fromjson')
def fromjson_filter(value):
    """Convert JSON string to Python object"""
    if not value or value == 'null':
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

@app.template_filter('length')
def length_filter(value):
    """Get length of list or string"""
    if not value:
        return 0
    return len(value)

# Encryption key for SIAKAD credentials
ENCRYPTION_KEY = app.config.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key()
    print("⚠️  Warning: Using auto-generated encryption key. Set ENCRYPTION_KEY in environment for production.")

cipher_suite = Fernet(ENCRYPTION_KEY)

# Global variable to track active WAR sessions
active_sessions = {}
celery_tasks = {}  # Track Celery task IDs for users

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    settings = db.relationship('UserSettings', backref='user', uselist=False)
    war_sessions = db.relationship('WarSession', backref='user')
    activity_logs = db.relationship('ActivityLog', backref='user')

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ci_session = db.Column(db.Text)  # Stored encrypted
    cf_clearance = db.Column(db.Text)  # Stored encrypted
    telegram_bot_token = db.Column(db.Text)
    telegram_chat_id = db.Column(db.Text)
    target_courses = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_ci_session(self, value):
        """Set ci_session with encryption"""
        self.ci_session = encrypt_cookie(value) if value else None
    
    def get_ci_session(self):
        """Get decrypted ci_session"""
        return decrypt_cookie(self.ci_session) if self.ci_session else None
    
    def set_cf_clearance(self, value):
        """Set cf_clearance with encryption"""
        self.cf_clearance = encrypt_cookie(value) if value else None
    
    def get_cf_clearance(self):
        """Get decrypted cf_clearance"""
        return decrypt_cookie(self.cf_clearance) if self.cf_clearance else None
    
    def __repr__(self):
        return f"<UserSettings for user_id={self.user_id}>"

class WarSession(db.Model):
    __tablename__ = 'war_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='stopped')  # active, stopped, completed, error
    started_at = db.Column(db.DateTime)
    stopped_at = db.Column(db.DateTime)
    courses_obtained = db.Column(db.Text)  # JSON string
    total_attempts = db.Column(db.Integer, default=0)
    successful_attempts = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime)
    
    # Relationships
    activity_logs = db.relationship('ActivityLog', backref='war_session')

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('war_sessions.id'))
    level = db.Column(db.String(10), default='INFO')  # INFO, ERROR, WARNING, SUCCESS
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(30), nullable=False)  # e.g., AR25-11001
    course_name = db.Column(db.String(200), nullable=False)  # e.g., Studio Dasar 1
    class_type = db.Column(db.String(100), nullable=False)  # e.g., RA,RB,RC,RD
    class_id = db.Column(db.String(100), nullable=False, unique=True)  # e.g., 35634,35636,35638,35639
    semester = db.Column(db.String(20))  # e.g., 2025/2026-1
    sks = db.Column(db.Integer, default=0)
    faculty = db.Column(db.String(150))  # e.g., Fakultas Teknik - Informatika
    department = db.Column(db.String(150))  # e.g., 💻 INFORMATIKA (IF)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_courses')
    
    def __repr__(self):
        return f"<Course {self.course_code} ({self.class_type}) - {self.course_name}>"

# Forms
class LoginForm(FlaskForm):
    nim = StringField('NIM', validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    nim = StringField('NIM', validators=[DataRequired(), Length(min=5, max=20)])
    name = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Daftar')
    
    def validate_nim(self, nim):
        user = User.query.filter_by(nim=nim.data).first()
        if user:
            raise ValidationError('NIM sudah terdaftar. Silakan gunakan NIM lain.')

class SettingsForm(FlaskForm):
    ci_session = StringField('CI_SESSION Cookie', validators=[DataRequired(), Length(min=10)])
    cf_clearance = StringField('CF_CLEARANCE Cookie', validators=[DataRequired(), Length(min=10)])
    telegram_bot_token = StringField('Telegram Bot Token')
    telegram_chat_id = StringField('Telegram Chat ID')
    target_courses = SelectMultipleField('Target Mata Kuliah', choices=[])
    submit = SubmitField('Simpan Pengaturan')

class CourseForm(FlaskForm):
    course_code = StringField('Kode Mata Kuliah', validators=[DataRequired(), Length(min=5, max=20)], 
                             render_kw={"placeholder": "Contoh: AR25-11001"})
    course_name = StringField('Nama Mata Kuliah', validators=[DataRequired(), Length(min=5, max=200)], 
                             render_kw={"placeholder": "Contoh: Studio Dasar 1"})
    class_type = StringField('Kelas', validators=[DataRequired(), Length(min=1, max=10)], 
                            render_kw={"placeholder": "Contoh: RA, RB, RC"})
    class_id = StringField('Class ID SIAKAD', validators=[DataRequired(), Length(min=3, max=20)], 
                          render_kw={"placeholder": "Contoh: 37053"})
    sks = StringField('SKS', render_kw={"placeholder": "Contoh: 3"})
    faculty = StringField('Fakultas', render_kw={"placeholder": "Contoh: Fakultas Teknik"})
    department = StringField('Jurusan', render_kw={"placeholder": "Contoh: Teknik Arsitektur"})
    semester = StringField('Semester', render_kw={"placeholder": "Contoh: 2024/2025-1"})
    submit = SubmitField('Tambah Course')
    
    def validate_class_id(self, class_id):
        course = Course.query.filter_by(class_id=class_id.data).first()
        if course:
            raise ValidationError('Class ID sudah ada. Silakan gunakan Class ID lain.')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def encrypt_password(password):
    """Encrypt SIAKAD password"""
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    """Decrypt SIAKAD password"""
    try:
        return cipher_suite.decrypt(encrypted_password.encode()).decode()
    except:
        return None

def encrypt_cookie(cookie_value):
    """Encrypt sensitive cookie values (ci_session, cf_clearance)"""
    if not cookie_value:
        return None
    try:
        return cipher_suite.encrypt(cookie_value.encode()).decode()
    except Exception as e:
        print(f"⚠️ Warning: Failed to encrypt cookie: {e}")
        return cookie_value  # Return original if encryption fails

def decrypt_cookie(encrypted_cookie):
    """Decrypt sensitive cookie values"""
    if not encrypted_cookie:
        return None
    try:
        return cipher_suite.decrypt(encrypted_cookie.encode()).decode()
    except Exception as e:
        print(f"⚠️ Warning: Failed to decrypt cookie: {e}")
        return encrypted_cookie  # Return as-is if decryption fails (might be unencrypted)

def log_activity(user_id, message, level='INFO', session_id=None):
    """Log user activity"""
    log = ActivityLog(
        user_id=user_id,
        session_id=session_id,
        level=level,
        message=message
    )
    db.session.add(log)
    db.session.commit()

def load_course_list():
    """Load available courses from database with fallback to COURSE_LIST.md"""
    try:
        # First, try to load from database
        courses_from_db = Course.query.filter_by(is_active=True).order_by(Course.course_code, Course.class_type).all()
        
        if courses_from_db:
            # Convert database courses to form choices format
            courses = []
            for course in courses_from_db:
                course_label = f"{course.course_code} ({course.class_type}) - {course.course_name}"
                if course.sks:
                    course_label += f" [{course.sks} SKS]"
                courses.append((course.class_id, course_label))
            
            print(f"✅ Loaded {len(courses)} courses from database")
            return courses
        
        # If no courses in database, try to migrate from COURSE_LIST.md
        print("⚠️  No courses found in database, attempting to migrate from COURSE_LIST.md...")
        migrate_courses_from_md()
        
        # Try database again after migration
        courses_from_db = Course.query.filter_by(is_active=True).order_by(Course.course_code, Course.class_type).all()
        if courses_from_db:
            courses = []
            for course in courses_from_db:
                course_label = f"{course.course_code} ({course.class_type}) - {course.course_name}"
                if course.sks:
                    course_label += f" [{course.sks} SKS]"
                courses.append((course.class_id, course_label))
            print(f"✅ Loaded {len(courses)} courses from database after migration")
            return courses
        
        # If migration failed, fallback to MD file parsing
        print("⚠️  Migration failed, falling back to direct MD parsing...")
        return load_course_list_from_md()
            
    except Exception as e:
        print(f"⚠️  Error loading courses from database: {e}")
        print("   Falling back to MD file parsing...")
        # Fallback to original MD file parsing
        return load_course_list_from_md()
    
def migrate_courses_from_md():
    """Migrate courses from GitHub COURSE_LIST.md URL to database, with support for faculty/department and auto semester."""
    try:
        import requests

        def get_current_semester():
            now = datetime.now()
            year = now.year
            month = now.month
            # Assume semester 1: Aug-Jan, semester 2: Feb-Jul
            if month >= 8 or month <= 1:
                # Odd semester (Ganjil)
                sem = 1
                if month == 1:
                    year -= 1  # Jan is still previous academic year
            else:
                # Even semester (Genap)
                sem = 2
            if sem == 1:
                return f"{year}/{year+1}-1"
            else:
                return f"{year-1}/{year}-2"

        # Load course data from GitHub URL
        course_url = "https://raw.githubusercontent.com/EgiStr/itera-warkrs-siakad-flask/refs/heads/main/COURSE_LIST.md"
        print(f"📚 Loading course data from GitHub: {course_url}")
        
        response = requests.get(course_url, timeout=30)
        response.raise_for_status()
        content = response.text
            
        lines = content.split('\n')
        in_table = False
        courses_added = 0
        current_department = None
        current_faculty = None
        semester = get_current_semester()
        
        for line in lines:
            line = line.strip()
            
            # Detect department/faculty section (e.g., ## 📊 SAINS DATA (SD))
            if line.startswith('##'):
                # Set department/faculty for following courses
                current_department = line.replace('##', '').strip()
                # Optionally, parse faculty from department name if needed
                # Example: "📊 SAINS DATA (SD)" -> department: "SAINS DATA (SD)"
                # You can set current_faculty here if you want to map by section
                continue

            # Skip empty lines and headers
            if not line or line.startswith('#') or line.startswith('-') or line.startswith('**'):
                continue
            
            # Detect table start (header row)
            if 'Kode Mata Kuliah' in line and 'Nama Mata Kuliah' in line:
                in_table = True
                continue
            
            # Skip table separator row
            if in_table and line.startswith('|--'):
                continue
            
            # Parse table rows
            if in_table and line.startswith('|') and line.endswith('|'):
                parts = [part.strip() for part in line.split('|')]
                
                # Table format: | Kode | Nama | Kelas | Class ID |
                if len(parts) >= 5:
                    kode = parts[1].strip()
                    nama = parts[2].strip()
                    kelas = parts[3].strip()
                    class_id = parts[4].strip()
                    
                    if kode and nama and kelas and class_id:
                        # Check if course already exists
                        existing_course = Course.query.filter_by(class_id=class_id).first()
                        if not existing_course:
                            # Create new course - need a default user for created_by
                            system_user = User.query.filter_by(nim='SYSTEM').first()
                            if not system_user:
                                system_user = User.query.first()
                            
                            # If still no user, create a system user
                            if not system_user:
                                system_user = User(
                                    nim='SYSTEM',
                                    name='System User',
                                    password_hash=bcrypt.generate_password_hash('system_password').decode('utf-8')
                                )
                                db.session.add(system_user)
                                db.session.flush()  # Get the ID
                            
                            # Determine faculty from course code
                            faculty_code = kode[:2] if kode else ''
                            faculty_map = {
                                'AR': 'Fakultas Teknik - Arsitektur',
                                'IF': 'Fakultas Teknik - Informatika', 
                                'TK': 'Fakultas Teknik - Teknik Kimia',
                                'TS': 'Fakultas Teknik - Teknik Sipil',
                                'TI': 'Fakultas Teknik - Teknik Industri',
                                'TM': 'Fakultas Teknik - Teknik Mesin',
                                'TL': 'Fakultas Teknik - Teknik Lingkungan',
                                'TE': 'Fakultas Teknik - Teknik Elektro',
                                'GL': 'Fakultas Teknik - Teknik Geologi',
                                'PW': 'Fakultas Teknik - Perencanaan Wilayah',
                                'SD': 'Fakultas Teknik - Sains Data',
                                'BT': 'Fakultas Teknobiologi',
                                'KP': 'Fakultas Teknik - Kepengurusan'
                            }
                            
                            faculty = faculty_map.get(faculty_code, current_faculty or 'Lainnya')
                            
                            new_course = Course(
                                course_code=kode,
                                course_name=nama,
                                class_type=kelas,
                                class_id=class_id,
                                created_by=system_user.id,
                                department=current_department,
                                faculty=faculty,
                                semester=semester
                            )
                            db.session.add(new_course)
                            courses_added += 1
            
            # Stop parsing if we hit end of table section
            if in_table and line.startswith('---'):
                break
        
        if courses_added > 0:
            db.session.commit()
            print(f"✅ Migrated {courses_added} courses from COURSE_LIST.md to database")
        else:
            print("⚠️  No courses found in COURSE_LIST.md to migrate")
            
    except requests.RequestException as e:
        print(f"⚠️  Failed to load course data from GitHub: {e}")
        print("⚠️  Using fallback courses due to network error")
    except FileNotFoundError:
        print("⚠️  COURSE_LIST.md not found for migration")
    except Exception as e:
        print(f"⚠️  Error migrating courses from GitHub: {e}")
        db.session.rollback()

def load_course_list_from_md():
    """Fallback function to load courses from GitHub COURSE_LIST.md URL"""
    try:
        import requests
        
        # Load course data from GitHub URL
        course_url = "https://raw.githubusercontent.com/EgiStr/itera-warkrs-siakad-flask/refs/heads/main/COURSE_LIST.md"
        print(f"📚 Loading course data from GitHub: {course_url}")
        
        response = requests.get(course_url, timeout=30)
        response.raise_for_status()
        content = response.text
        
        courses = []
        
        # Parse markdown table format
        lines = content.split('\n')
        in_table = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('#') or line.startswith('-') or line.startswith('**'):
                continue
            
            # Detect table start (header row)
            if 'Kode Mata Kuliah' in line and 'Nama Mata Kuliah' in line:
                in_table = True
                continue
            
            # Skip table separator row
            if in_table and line.startswith('|--'):
                continue
            
            # Parse table rows
            if in_table and line.startswith('|') and line.endswith('|'):
                parts = [part.strip() for part in line.split('|')]
                
                # Table format: | Kode | Nama | Kelas | Class ID |
                if len(parts) >= 5:  # Including empty first and last parts from split
                    kode = parts[1].strip()
                    nama = parts[2].strip()
                    kelas = parts[3].strip()
                    class_id = parts[4].strip()
                    
                    if kode and nama and kelas and class_id:
                        # Create course identifier with class
                        course_label = f"{kode} ({kelas}) - {nama}"
                        courses.append((class_id, course_label))
            
            # Stop parsing if we hit end of table section
            if in_table and line.startswith('---'):
                break
        
        # Sort courses by name for better UX
        courses.sort(key=lambda x: x[1])
        return courses
        
    except requests.RequestException as e:
        print(f"⚠️  Failed to load course data from GitHub: {e}")
        print("⚠️  Using fallback courses due to network error")
        # Fallback to some default courses
        return [
            ('37053', 'AR25-11001 (RA) - Studio Dasar 1'),
            ('37055', 'AR25-11001 (RB) - Studio Dasar 1'),
            ('37056', 'AR25-11001 (RC) - Studio Dasar 1'),
            ('35998', 'IF25-40033 - Algoritma dan Pemrograman'),
            ('36847', 'TK25-40001 - Teknik Kimia Dasar')
        ]
    except FileNotFoundError:
        print("⚠️  COURSE_LIST.md not found, using fallback courses")
        # Fallback to some default courses
        return [
            ('37053', 'AR25-11001 (RA) - Studio Dasar 1'),
            ('37055', 'AR25-11001 (RB) - Studio Dasar 1'),
            ('37056', 'AR25-11001 (RC) - Studio Dasar 1'),
            ('35998', 'IF25-40033 - Algoritma dan Pemrograman'),
            ('36847', 'TK25-40001 - Teknik Kimia Dasar')
        ]
    except Exception as e:
        print(f"⚠️  Error parsing course data from GitHub: {e}")
        return [
            ('fallback1', 'Error loading courses - please check network connection'),
            ('fallback2', 'Using fallback course list')
        ]

# WAR KRS Background Process
def run_war_process(user_id, session_id):
    """Run WAR KRS process in background thread - simplified version"""
    global active_sessions
    
    # CRITICAL: Set up Flask application context for database access
    with app.app_context():
        try:
            # Get user settings
            user = User.query.get(user_id)
            settings = user.settings
            
            if not settings:
                log_activity(user_id, "User settings not found", "ERROR", session_id)
                return
            
            # Get decrypted cookie values
            ci_session_decrypted = settings.get_ci_session()
            cf_clearance_decrypted = settings.get_cf_clearance()
            
            if not ci_session_decrypted or not cf_clearance_decrypted:
                log_activity(user_id, "SIAKAD cookies not configured or failed to decrypt", "ERROR", session_id)
                return
            
            # Setup cookies for SIAKAD session using decrypted values
            cookies = {
                'ci_session': ci_session_decrypted,
                'cf_clearance': cf_clearance_decrypted
            }
            
            log_activity(user_id, "Successfully decrypted SIAKAD cookies for WAR process", "INFO", session_id)
            
            # Parse target courses
            target_courses_list = json.loads(settings.target_courses) if settings.target_courses else []
            
            if not target_courses_list:
                log_activity(user_id, "No target courses selected", "ERROR", session_id)
                return
            
            # Update session status
            war_session = WarSession.query.get(session_id)
            war_session.status = 'active'
            war_session.started_at = datetime.utcnow()
            war_session.last_activity = datetime.utcnow()
            db.session.commit()
            
            log_activity(user_id, f"WAR KRS process started for {len(target_courses_list)} courses using cookies", "INFO", session_id)
            
            # Mark session as active FIRST - before any potential failures
            active_sessions[user_id] = {
                'session_id': session_id,
                'status': 'active',
                'started_at': datetime.utcnow(),
                'stop_requested': False
            }
            
            log_activity(user_id, f"Session {user_id} marked as active in active_sessions", "INFO", session_id)
            
            # Try to use existing controller with fallback to simplified approach
            try:
                # Attempt to use existing business logic
                from config.settings import Config
                config = Config()
                default_settings = config.get_all()
                urls = default_settings.get('siakad_urls', {})
                
                log_activity(user_id, f"Config loaded successfully. URLs: {list(urls.keys())}", "INFO", session_id)
                
                # target_courses_list now contains class_ids (from the form)
                # Convert to format expected by existing controller (course_code -> class_id)
                target_courses_dict = {}
                
                # Load course list to get mapping
                available_courses = load_course_list()
                course_id_to_info = {class_id: label for class_id, label in available_courses}
                
                for class_id in target_courses_list:
                    if class_id in course_id_to_info:
                        # Extract course code from label (e.g., "AR25-11001 (RA) - Studio Dasar 1")
                        course_info = course_id_to_info[class_id]
                        course_code = course_info.split(' ')[0]  # Get "AR25-11001"
                        target_courses_dict[course_code] = class_id
                    else:
                        # Fallback: use class_id as both key and value
                        target_courses_dict[class_id] = class_id
                
                log_activity(user_id, f"Target courses configured: {list(target_courses_dict.keys())}", "INFO", session_id)
                
                # Setup Telegram configuration
                telegram_config = None
                if settings.telegram_bot_token and settings.telegram_chat_id:
                    telegram_config = {
                        'bot_token': settings.telegram_bot_token,
                        'chat_id': settings.telegram_chat_id
                    }
                    log_activity(user_id, "Telegram notifications configured", "INFO", session_id)
                
                # Initialize controller with existing business logic
                log_activity(user_id, "Initializing WARKRSController...", "INFO", session_id)
                
                controller = WARKRSController(
                    cookies=cookies,
                    urls=urls,
                    target_courses=target_courses_dict,
                    settings=default_settings,
                    telegram_config=telegram_config,
                    debug_mode=False
                )
                
                log_activity(user_id, f"Controller initialized successfully. Remaining targets: {len(controller.remaining_targets)}", "SUCCESS", session_id)
                
                # Send Telegram start notification
                if telegram_config:
                    try:
                        notifier = TelegramNotifier(
                            bot_token=telegram_config['bot_token'],
                            chat_id=telegram_config['chat_id']
                        )
                        notifier.notify_start(list(target_courses_dict.keys()))
                        log_activity(user_id, "Telegram start notification sent", "INFO", session_id)
                    except Exception as tg_error:
                        log_activity(user_id, f"Telegram start notification failed: {str(tg_error)}", "WARNING", session_id)
                
                # Validate controller setup
                if not hasattr(controller, 'remaining_targets') or len(controller.remaining_targets) == 0:
                    log_activity(user_id, "Warning: Controller has no remaining targets", "WARNING", session_id)
                
                if not hasattr(controller, 'session') or controller.session is None:
                    log_activity(user_id, "Warning: Controller session not initialized properly", "WARNING", session_id)
                
                # Main WAR loop using existing controller
                successful_courses = []
                cycle_delay = default_settings.get('cycle_delay', 5)
                
                log_activity(user_id, f"Starting WAR loop with {len(controller.remaining_targets)} target courses", "INFO", session_id)
                
                while (active_sessions.get(user_id, {}).get('status') == 'active' and 
                       len(controller.remaining_targets) > 0):
                    
                    # Check if stop was requested
                    if active_sessions.get(user_id, {}).get('stop_requested'):
                        log_activity(user_id, "Stop requested - breaking WAR loop", "INFO", session_id)
                        break
                    
                    try:
                        log_activity(user_id, f"Starting cycle {controller.cycle_count + 1}", "INFO", session_id)
                        
                        # Run single cycle using existing controller logic
                        session_valid, session_status, successful_this_cycle, failed_this_cycle = controller.run_single_cycle()
                        
                        log_activity(user_id, f"Cycle {controller.cycle_count} completed. Valid: {session_valid}, Success: {len(successful_this_cycle) if successful_this_cycle else 0}, Failed: {len(failed_this_cycle) if failed_this_cycle else 0}", "INFO", session_id)
                        
                        # Update session stats
                        war_session.total_attempts += 1
                        war_session.last_activity = datetime.utcnow()
                        
                        if successful_this_cycle:
                            war_session.successful_attempts += 1
                            successful_courses.extend(successful_this_cycle)
                            
                            # Remove obtained courses from remaining targets
                            for course in successful_this_cycle:
                                controller.remaining_targets.discard(course)
                            
                            log_activity(user_id, f"Cycle {controller.cycle_count} completed successfully. Obtained: {', '.join(successful_this_cycle)}", "SUCCESS", session_id)
                            
                            # Send Telegram notification for successful courses
                            if telegram_config:
                                try:
                                    notifier = TelegramNotifier(
                                        bot_token=telegram_config['bot_token'],
                                        chat_id=telegram_config['chat_id']
                                    )
                                    for course in successful_this_cycle:
                                        notifier.notify_course_success(course)
                                    log_activity(user_id, f"Telegram notifications sent for {len(successful_this_cycle)} courses", "INFO", session_id)
                                except Exception as tg_error:
                                    log_activity(user_id, f"Telegram notification failed: {str(tg_error)}", "WARNING", session_id)
                        
                        if failed_this_cycle:
                            log_activity(user_id, f"Cycle {controller.cycle_count} - Failed courses: {', '.join(failed_this_cycle)}", "WARNING", session_id)
                        
                        # Handle session errors
                        if not session_valid:
                            log_activity(user_id, f"Session validation failed: {session_status.get('recommended_action', 'unknown')}", "ERROR", session_id)
                            
                            # Send Telegram session warning
                            if telegram_config:
                                try:
                                    notifier = TelegramNotifier(
                                        bot_token=telegram_config['bot_token'],
                                        chat_id=telegram_config['chat_id']
                                    )
                                    notifier.notify_session_warning(session_status, controller.cycle_count)
                                    log_activity(user_id, "Telegram session warning sent", "INFO", session_id)
                                except Exception as tg_error:
                                    log_activity(user_id, f"Telegram session warning failed: {str(tg_error)}", "WARNING", session_id)
                            
                            # If critical session error, stop the process
                            if session_status.get('recommended_action') == 'stop_and_reauth':
                                log_activity(user_id, "Critical session error - cookies may be expired. Please update cookies in settings.", "ERROR", session_id)
                                
                                # Send Telegram error notification
                                if telegram_config:
                                    try:
                                        notifier = TelegramNotifier(
                                            bot_token=telegram_config['bot_token'],
                                            chat_id=telegram_config['chat_id']
                                        )
                                        notifier.notify_error("Session expired - please update SIAKAD cookies in settings")
                                        log_activity(user_id, "Telegram session expired notification sent", "INFO", session_id)
                                    except Exception as tg_error:
                                        log_activity(user_id, f"Telegram session expired notification failed: {str(tg_error)}", "WARNING", session_id)
                                
                                break
                        
                        # Update courses obtained
                        war_session.courses_obtained = json.dumps(successful_courses)
                        db.session.commit()
                        
                        # Check if all courses obtained
                        if not controller.remaining_targets:
                            log_activity(user_id, "All target courses obtained! WAR process completed.", "SUCCESS", session_id)
                            break
                        
                        # Wait before next cycle
                        log_activity(user_id, f"Waiting {cycle_delay} seconds before next cycle", "INFO", session_id)
                        time.sleep(cycle_delay)
                        
                    except Exception as e:
                        log_activity(user_id, f"Error in cycle {controller.cycle_count}: {str(e)}", "ERROR", session_id)
                        
                        # Continue to next cycle after error
                        time.sleep(10)  # Wait longer after error
                
                # Update final session status
                war_session.status = 'completed' if not controller.remaining_targets else 'stopped'
                war_session.stopped_at = datetime.utcnow()
                db.session.commit()
                
                final_message = f"WAR process ended. Obtained {len(successful_courses)} courses in {controller.cycle_count} cycles."
                log_activity(user_id, final_message, "INFO", session_id)
                
                # Send Telegram completion notification
                if telegram_config:
                    try:
                        notifier = TelegramNotifier(
                            bot_token=telegram_config['bot_token'],
                            chat_id=telegram_config['chat_id']
                        )
                        if successful_courses:
                            notifier.notify_all_completed(successful_courses, f"{controller.cycle_count} cycles")
                        else:
                            notifier.notify_error("WAR process completed without obtaining any courses")
                        log_activity(user_id, "Telegram completion notification sent", "INFO", session_id)
                    except Exception as tg_error:
                        log_activity(user_id, f"Telegram completion notification failed: {str(tg_error)}", "WARNING", session_id)
                
            except Exception as controller_error:
                # Fallback to simplified approach if controller fails
                log_activity(user_id, f"Controller initialization failed: {str(controller_error)}", "WARNING", session_id)
                log_activity(user_id, f"Error details: {type(controller_error).__name__}", "WARNING", session_id)
                log_activity(user_id, "Falling back to simplified WAR process", "INFO", session_id)
                
                # Simplified WAR process as fallback
                run_simplified_war_process(user_id, session_id, target_courses_list, cookies, telegram_config)
            
        except Exception as e:
            # Handle any unexpected errors
            war_session = WarSession.query.get(session_id)
            war_session.status = 'error'
            war_session.stopped_at = datetime.utcnow()
            db.session.commit()
            
            log_activity(user_id, f"WAR process failed with error: {str(e)}", "ERROR", session_id)
        
        finally:
            # Always remove from active sessions
            if user_id in active_sessions:
                del active_sessions[user_id]

def run_simplified_war_process(user_id, session_id, target_courses_list, cookies, telegram_config=None):
    """Simplified WAR process as fallback"""
    # This function is called from within app context, so no need to recreate it
    try:
        import requests
        from bs4 import BeautifulSoup
        
        war_session = WarSession.query.get(session_id)
        successful_courses = []
        cycle_count = 0
        max_cycles = 10  # Limit cycles for testing
        
        # Basic session for requests
        session = requests.Session()
        session.cookies.update(cookies)
        
        # SIAKAD URLs (hardcoded fallback)
        krs_url = "https://siakad.itera.ac.id/mahasiswa/krsbaru/pilihmk"
        
        log_activity(user_id, f"Starting simplified WAR process for {len(target_courses_list)} courses", "INFO", session_id)
        
        # Send Telegram start notification for simplified process
        if telegram_config:
            try:
                notifier = TelegramNotifier(
                    bot_token=telegram_config['bot_token'],
                    chat_id=telegram_config['chat_id']
                )
                notifier.notify_start(target_courses_list)
                log_activity(user_id, "Telegram start notification sent (simplified)", "INFO", session_id)
            except Exception as tg_error:
                log_activity(user_id, f"Telegram start notification failed (simplified): {str(tg_error)}", "WARNING", session_id)
        
        while (active_sessions.get(user_id, {}).get('status') == 'active' and 
               len(target_courses_list) > len(successful_courses) and
               cycle_count < max_cycles):
            
            cycle_count += 1
            
            # Check if stop was requested
            if active_sessions.get(user_id, {}).get('stop_requested'):
                log_activity(user_id, "Stop requested in simplified WAR process", "INFO", session_id)
                break
            
            log_activity(user_id, f"Simplified cycle {cycle_count} started", "INFO", session_id)
            
            for class_id in target_courses_list:
                if class_id in successful_courses:
                    continue  # Skip already obtained courses
                
                try:
                    # Try to register for this course
                    # This is a simplified implementation - you may need to adjust based on SIAKAD's actual API
                    
                    log_activity(user_id, f"Attempting to register course {class_id}", "INFO", session_id)
                    
                    response = session.post(krs_url, data={
                        'class_id': class_id,
                        'action': 'add'
                    }, timeout=10)
                    
                    if response.status_code == 200:
                        # Check if registration was successful
                        # This would need to be adjusted based on SIAKAD's response format
                        if 'berhasil' in response.text.lower() or 'success' in response.text.lower():
                            successful_courses.append(class_id)
                            log_activity(user_id, f"Successfully registered for course {class_id}", "SUCCESS", session_id)
                            
                            # Send Telegram notification for successful course
                            if telegram_config:
                                try:
                                    notifier = TelegramNotifier(
                                        bot_token=telegram_config['bot_token'],
                                        chat_id=telegram_config['chat_id']
                                    )
                                    notifier.notify_course_success(class_id)
                                    log_activity(user_id, f"Telegram course success notification sent for {class_id}", "INFO", session_id)
                                except Exception as tg_error:
                                    log_activity(user_id, f"Telegram course notification failed: {str(tg_error)}", "WARNING", session_id)
                        else:
                            log_activity(user_id, f"Registration failed for course {class_id} - response indicates failure", "WARNING", session_id)
                    else:
                        log_activity(user_id, f"HTTP error {response.status_code} for course {class_id}", "ERROR", session_id)
                
                except Exception as e:
                    log_activity(user_id, f"Error registering course {class_id}: {str(e)}", "ERROR", session_id)
                
                # Small delay between course attempts
                time.sleep(2)
            
            # Update session stats
            war_session.total_attempts += 1
            war_session.successful_attempts = len(successful_courses)
            war_session.courses_obtained = json.dumps(successful_courses)
            war_session.last_activity = datetime.utcnow()
            db.session.commit()
            
            log_activity(user_id, f"Cycle {cycle_count} completed. Total successful: {len(successful_courses)}/{len(target_courses_list)}", "INFO", session_id)
            
            # Check if all courses obtained
            if len(successful_courses) >= len(target_courses_list):
                log_activity(user_id, "All target courses obtained! Simplified WAR process completed.", "SUCCESS", session_id)
                break
            
            # Wait before next cycle
            time.sleep(5)
        
        # Update final session status
        war_session.status = 'completed' if len(successful_courses) >= len(target_courses_list) else 'stopped'
        war_session.stopped_at = datetime.utcnow()
        db.session.commit()
        
        final_message = f"Simplified WAR process ended. Obtained {len(successful_courses)}/{len(target_courses_list)} courses in {cycle_count} cycles."
        log_activity(user_id, final_message, "INFO", session_id)
        
        # Send Telegram completion notification for simplified process
        if telegram_config:
            try:
                notifier = TelegramNotifier(
                    bot_token=telegram_config['bot_token'],
                    chat_id=telegram_config['chat_id']
                )
                if successful_courses:
                    notifier.notify_all_completed(successful_courses, f"{cycle_count} cycles")
                else:
                    notifier.notify_error("Simplified WAR process completed without obtaining any courses")
                log_activity(user_id, "Telegram completion notification sent (simplified)", "INFO", session_id)
            except Exception as tg_error:
                log_activity(user_id, f"Telegram completion notification failed (simplified): {str(tg_error)}", "WARNING", session_id)
        
    except Exception as e:
        log_activity(user_id, f"Simplified WAR process failed: {str(e)}", "ERROR", session_id)

# Routes
@app.route('/')
@login_required
def dashboard():
    """Main dashboard showing WAR status and controls"""
    # Get current WAR session
    current_session = WarSession.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).first()
    
    # Get recent activity logs
    recent_logs = ActivityLog.query.filter_by(
        user_id=current_user.id
    ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    # Get session status
    session_status = active_sessions.get(current_user.id, {})
    
    # Get user settings
    settings = current_user.settings
    
    # Parse JSON data for template
    target_courses = []
    obtained_courses = []
    
    if settings and settings.target_courses:
        try:
            target_courses = json.loads(settings.target_courses)
        except (json.JSONDecodeError, TypeError):
            target_courses = []
    
    if current_session and current_session.courses_obtained:
        try:
            obtained_courses = json.loads(current_session.courses_obtained)
        except (json.JSONDecodeError, TypeError):
            obtained_courses = []
    
    return render_template('dashboard.html',
                         current_session=current_session,
                         recent_logs=recent_logs,
                         session_status=session_status,
                         settings=settings,
                         target_courses=target_courses,
                         obtained_courses=obtained_courses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nim=form.nim.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login berhasil!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('NIM atau password salah.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(nim=form.nim.data, name=form.name.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # Create default settings
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    form = SettingsForm()
    
    # Load course choices
    form.target_courses.choices = load_course_list()
    
    if form.validate_on_submit():
        settings = current_user.settings
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.session.add(settings)
        
        # Update settings with encryption for sensitive data
        settings.set_ci_session(form.ci_session.data)
        settings.set_cf_clearance(form.cf_clearance.data)
        settings.telegram_bot_token = form.telegram_bot_token.data
        settings.telegram_chat_id = form.telegram_chat_id.data
        settings.target_courses = json.dumps(form.target_courses.data)
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(current_user.id, "Settings updated successfully (cookies encrypted)")
        flash('Pengaturan berhasil disimpan! Cookies telah dienkripsi untuk keamanan.', 'success')
        return redirect(url_for('settings'))
    
    # Load current settings with decryption for display
    if current_user.settings:
        form.ci_session.data = current_user.settings.get_ci_session()
        form.cf_clearance.data = current_user.settings.get_cf_clearance()
        form.telegram_bot_token.data = current_user.settings.telegram_bot_token
        form.telegram_chat_id.data = current_user.settings.telegram_chat_id
        if current_user.settings.target_courses:
            form.target_courses.data = json.loads(current_user.settings.target_courses)
    
    return render_template('settings.html', form=form)

@app.route('/war/start', methods=['POST'])
@login_required
def start_war():
    """Start WAR process"""
    # Check if already running
    if current_user.id in active_sessions:
        flash('WAR process sudah berjalan!', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check settings
    if not current_user.settings or not current_user.settings.ci_session:
        flash('Harap lengkapi cookies SIAKAD terlebih dahulu.', 'error')
        return redirect(url_for('settings'))
    
    # Check target courses
    if not current_user.settings.target_courses:
        flash('Harap pilih mata kuliah target terlebih dahulu.', 'error')
        return redirect(url_for('settings'))
    
    # Create new WAR session
    war_session = WarSession(user_id=current_user.id)
    db.session.add(war_session)
    db.session.commit()
    
    # Log start attempt
    log_activity(current_user.id, "User initiated WAR KRS process from dashboard", "INFO", war_session.id)
    
    if CELERY_AVAILABLE:
        # Use Celery for background processing (RECOMMENDED for production)
        try:
            # Get user settings and prepare task parameters
            settings = current_user.settings
            
            if not settings:
                flash('User settings not found', 'error')
                return redirect(url_for('settings'))
            
            # Get decrypted cookies
            cookies = {
                'ci_session': settings.get_ci_session(),
                'cf_clearance': settings.get_cf_clearance()
            }
            
            if not cookies['ci_session'] or not cookies['cf_clearance']:
                flash('SIAKAD cookies tidak valid atau gagal didekripsi', 'error')
                return redirect(url_for('settings'))
            
            # Get configuration
            from config.settings import Config
            config = Config()
            default_settings = config.get_all()
            urls = default_settings.get('siakad_urls', {})
            
            # Parse target courses
            target_courses_list = json.loads(settings.target_courses) if settings.target_courses else []
            
            if not target_courses_list:
                flash('No target courses selected', 'error')
                return redirect(url_for('settings'))
            
            # Convert target courses to expected format
            available_courses = load_course_list()
            course_id_to_info = {class_id: label for class_id, label in available_courses}
            
            target_courses_dict = {}
            for class_id in target_courses_list:
                if class_id in course_id_to_info:
                    course_info = course_id_to_info[class_id]
                    course_code = course_info.split(' ')[0]  # Get course code
                    target_courses_dict[course_code] = class_id
                else:
                    target_courses_dict[class_id] = class_id
            
            # Setup Telegram configuration
            telegram_config = None
            if settings.telegram_bot_token and settings.telegram_chat_id:
                telegram_config = {
                    'bot_token': settings.telegram_bot_token,
                    'chat_id': settings.telegram_chat_id
                }
            
            # Submit task to Celery
            task = run_war_task.delay(
                user_id=current_user.id,
                session_id=war_session.id,
                cookies=cookies,
                urls=urls,
                target_courses=target_courses_dict,
                settings=default_settings,
                telegram_config=telegram_config
            )
            
            # Track task
            celery_tasks[current_user.id] = {
                'task_id': task.id,
                'session_id': war_session.id,
                'started_at': datetime.utcnow(),
                'status': 'queued'
            }
            
            # Update session status  
            active_sessions[current_user.id] = {
                'session_id': war_session.id,
                'status': 'active',
                'started_at': datetime.utcnow(),
                'stop_requested': False,
                'task_id': task.id
            }
            
            flash(f'WAR KRS process berhasil dimulai dengan Celery! Task ID: {task.id[:8]}...', 'success')
            log_activity(current_user.id, f"Celery WAR task started with ID {task.id}", "SUCCESS", war_session.id)
            
        except Exception as e:
            flash(f'Gagal memulai WAR process dengan Celery: {str(e)}', 'error')
            log_activity(current_user.id, f"Celery WAR task failed: {str(e)}", "ERROR", war_session.id)
    else:
        # Use traditional background thread approach for local development
        # Start background thread
        thread = threading.Thread(target=run_war_process, args=(current_user.id, war_session.id))
        thread.daemon = True
        thread.start()
        
        # Give thread a moment to start and check if it's actually running
        time.sleep(2)
        
        if current_user.id in active_sessions:
            flash('WAR KRS process berhasil dimulai dengan threading!', 'success')
            log_activity(current_user.id, "WAR KRS background thread confirmed active", "SUCCESS", war_session.id)
        else:
            flash('Gagal memulai WAR process. Periksa logs untuk detail.', 'error')
            log_activity(current_user.id, "WAR KRS background thread failed to become active", "ERROR", war_session.id)
    
    return redirect(url_for('dashboard'))

@app.route('/war/stop', methods=['POST'])
@login_required
def stop_war():
    """Stop WAR process"""
    
    if CELERY_AVAILABLE and current_user.id in celery_tasks:
        # Stop Celery task
        try:
            task_info = celery_tasks[current_user.id]
            task_id = task_info['task_id']
            
            # Revoke the task
            celery_app.control.revoke(task_id, terminate=True)
            
            # Send stop signal via Celery task
            stop_task = stop_war_task.delay(current_user.id)
            
            # Clean up tracking
            del celery_tasks[current_user.id]
            if current_user.id in active_sessions:
                del active_sessions[current_user.id]
                
            flash(f'WAR process berhasil dihentikan! Stop task ID: {stop_task.id[:8]}...', 'success')
            log_activity(current_user.id, f"Celery WAR task stopped: {task_id}", "INFO")
            
        except Exception as e:
            flash(f'Error menghentikan Celery task: {str(e)}', 'error')
            log_activity(current_user.id, f"Error stopping Celery task: {str(e)}", "ERROR")
            
    elif current_user.id in active_sessions:
        # Stop threading-based task
        active_sessions[current_user.id]['stop_requested'] = True
        active_sessions[current_user.id]['status'] = 'stopping'
        flash('WAR process sedang dihentikan...', 'info')
        log_activity(current_user.id, "Threading WAR process stop requested", "INFO")
    else:
        flash('Tidak ada WAR process yang sedang berjalan.', 'warning')
    
    return redirect(url_for('dashboard'))

# API endpoints for Vercel compatibility
@app.route('/api/war/start', methods=['POST'])
@login_required
def api_start_war():
    """API endpoint to start WAR process (Vercel-compatible)"""
    try:
        # Check if already running
        if current_user.id in active_sessions:
            return jsonify({"error": "WAR process already running"}), 400
        
        # Check settings
        if not current_user.settings or not current_user.settings.ci_session:
            return jsonify({"error": "SIAKAD cookies not configured"}), 400
        
        # Check target courses
        if not current_user.settings.target_courses:
            return jsonify({"error": "No target courses selected"}), 400
        
        # Create new WAR session
        war_session = WarSession(user_id=current_user.id)
        db.session.add(war_session)
        db.session.commit()
        
        # Run serverless WAR process
        from vercel_war import run_war_process_serverless
        result = run_war_process_serverless(current_user.id, war_session.id, app, db)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/war/status')
@login_required 
def api_war_status():
    """API endpoint to check WAR process status"""
    try:
        # Get latest session
        latest_session = WarSession.query.filter_by(
            user_id=current_user.id
        ).order_by(WarSession.created_at.desc()).first()
        
        if latest_session:
            return jsonify({
                "session_id": latest_session.id,
                "status": latest_session.status,
                "started_at": latest_session.started_at.isoformat() if latest_session.started_at else None,
                "last_activity": latest_session.last_activity.isoformat() if latest_session.last_activity else None
            })
        else:
            return jsonify({"status": "no_session"})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs')
@login_required
def logs():
    """View activity logs"""
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.filter_by(
        user_id=current_user.id
    ).order_by(ActivityLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('logs.html', logs=logs)

@app.route('/api/status')
@login_required
def api_status():
    """API endpoint for real-time status updates"""
    
    # Check Celery task status if available
    if CELERY_AVAILABLE and current_user.id in celery_tasks:
        try:
            task_info = celery_tasks[current_user.id]
            task_id = task_info['task_id']
            
            # Get task result from Celery
            task = celery_app.AsyncResult(task_id)
            
            if task.state == 'PENDING':
                celery_status = 'queued'
                celery_info = {'message': 'Task is waiting to be processed'}
            elif task.state == 'PROGRESS':
                celery_status = 'active'
                celery_info = task.info or {}
            elif task.state == 'SUCCESS':
                celery_status = 'completed'
                celery_info = task.result or {}
            elif task.state == 'FAILURE':
                celery_status = 'error'
                celery_info = {'error': str(task.info)}
            else:
                celery_status = task.state.lower()
                celery_info = task.info or {}
                
            # Enhanced response with Celery information
            response = {
                'status': celery_status,
                'task_type': 'celery',
                'task_id': task_id,
                'session_active': celery_status in ['queued', 'active'],
                'celery_info': celery_info,
                'started_at': task_info.get('started_at').isoformat() if task_info.get('started_at') else None,
                'total_attempts': celery_info.get('cycle', 0),
                'successful_attempts': len(celery_info.get('successful_courses', [])),
                'obtained_courses': celery_info.get('successful_courses', []),
                'remaining_targets': celery_info.get('remaining_targets', []),
                'last_activity': celery_info.get('last_activity', '')
            }
            
            return jsonify(response)
            
        except Exception as e:
            # Fallback to database if Celery check fails
            pass
    
    # Fallback to existing logic
    session_status = active_sessions.get(current_user.id, {'status': 'stopped'})
    
    # Get current session from database
    current_session = WarSession.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).first()
    
    response = {
        'status': session_status.get('status', 'stopped'),
        'task_type': 'threading',
        'session_active': current_session is not None,
        'total_attempts': current_session.total_attempts if current_session else 0,
        'successful_attempts': current_session.successful_attempts if current_session else 0,
        'courses_obtained': json.loads(current_session.courses_obtained) if current_session and current_session.courses_obtained else [],
        'last_activity': current_session.last_activity.isoformat() if current_session and current_session.last_activity else None
    }
    
    return jsonify(response)

@app.route('/courses')
@login_required
def courses():
    """Manage courses page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    # Build query
    query = Course.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                Course.course_code.ilike(f'%{search}%'),
                Course.course_name.ilike(f'%{search}%'),
                Course.class_type.ilike(f'%{search}%'),
                Course.faculty.ilike(f'%{search}%'),
                Course.department.ilike(f'%{search}%')
            )
        )
    
    courses = query.order_by(Course.course_code, Course.class_type).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('courses.html', courses=courses, search=search)

@app.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    """Add new course"""
    form = CourseForm()
    
    if form.validate_on_submit():
        # Convert SKS to integer if provided
        sks = None
        if form.sks.data:
            try:
                sks = int(form.sks.data)
            except ValueError:
                sks = 0
        
        course = Course(
            course_code=form.course_code.data.upper(),
            course_name=form.course_name.data,
            class_type=form.class_type.data.upper(),
            class_id=form.class_id.data,
            sks=sks,
            faculty=form.faculty.data,
            department=form.department.data,
            semester=form.semester.data,
            created_by=current_user.id
        )
        
        db.session.add(course)
        db.session.commit()
        
        log_activity(current_user.id, f"Added new course: {course.course_code} ({course.class_type}) - {course.course_name}")
        flash(f'Course {course.course_code} ({course.class_type}) berhasil ditambahkan!', 'success')
        return redirect(url_for('courses'))
    
    return render_template('add_course.html', form=form)

@app.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Edit existing course"""
    course = Course.query.get_or_404(course_id)
    
    # Only allow creator or admin to edit
    if course.created_by != current_user.id:
        flash('Anda tidak memiliki izin untuk mengedit course ini.', 'error')
        return redirect(url_for('courses'))
    
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        # Convert SKS to integer if provided
        sks = None
        if form.sks.data:
            try:
                sks = int(form.sks.data)
            except ValueError:
                sks = 0
        
        course.course_code = form.course_code.data.upper()
        course.course_name = form.course_name.data
        course.class_type = form.class_type.data.upper()
        course.class_id = form.class_id.data
        course.sks = sks
        course.faculty = form.faculty.data
        course.department = form.department.data
        course.semester = form.semester.data
        course.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_activity(current_user.id, f"Edited course: {course.course_code} ({course.class_type}) - {course.course_name}")
        flash(f'Course {course.course_code} ({course.class_type}) berhasil diupdate!', 'success')
        return redirect(url_for('courses'))
    
    # Pre-fill form with current course data
    form.sks.data = str(course.sks) if course.sks else ""
    
    return render_template('edit_course.html', form=form, course=course)

@app.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    """Delete course (soft delete)"""
    course = Course.query.get_or_404(course_id)
    
    # Only allow creator to delete
    if course.created_by != current_user.id:
        flash('Anda tidak memiliki izin untuk menghapus course ini.', 'error')
        return redirect(url_for('courses'))
    
    course.is_active = False
    course.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_activity(current_user.id, f"Deleted course: {course.course_code} ({course.class_type}) - {course.course_name}")
    flash(f'Course {course.course_code} ({course.class_type}) berhasil dihapus!', 'success')
    
    return redirect(url_for('courses'))

@app.route('/api/courses')
@login_required
def api_courses():
    """API endpoint for course data with search and filtering"""
    search = request.args.get('search', '', type=str)
    faculty = request.args.get('faculty', '', type=str)
    
    # Build query
    query = Course.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                Course.course_code.ilike(f'%{search}%'),
                Course.course_name.ilike(f'%{search}%'),
                Course.class_type.ilike(f'%{search}%')
            )
        )
    
    if faculty:
        query = query.filter(Course.faculty.ilike(f'%{faculty}%'))
    
    courses = query.order_by(Course.course_code, Course.class_type).all()
    
    # Format response
    course_data = []
    for course in courses:
        course_label = f"{course.course_code} ({course.class_type}) - {course.course_name}"
        if course.sks:
            course_label += f" [{course.sks} SKS]"
        
        course_data.append({
            'value': course.class_id,
            'label': course_label,
            'course_code': f"{course.course_code} ({course.class_type})",
            'course_name': course.course_name,
            'faculty': course.faculty or 'Lainnya',
            'department': course.department or '',
            'sks': course.sks or 0,
            'semester': course.semester or '',
            'class_id': course.class_id
        })
    
    return jsonify({
        'courses': course_data,
        'total': len(course_data)
    })

@app.route('/api/faculties')
@login_required
def api_faculties():
    """API endpoint for available faculties"""
    faculties = db.session.query(Course.faculty).filter(
        Course.is_active == True,
        Course.faculty.isnot(None),
        Course.faculty != ''
    ).distinct().order_by(Course.faculty).all()
    
    faculty_list = [f[0] for f in faculties if f[0]]
    
    return jsonify({
        'faculties': faculty_list
    })

@app.route('/test_telegram', methods=['POST'])
@login_required
def test_telegram():
    """Test Telegram notification"""
    try:
        # Get user settings - ensure settings exist
        settings = current_user.settings
        if not settings:
            # Create default settings if they don't exist
            settings = UserSettings(
                user_id=current_user.id,
                cycle_delay=5,
                request_timeout=20,
                max_retries=3,
                telegram_bot_token='',
                telegram_chat_id=''
            )
            db.session.add(settings)
            db.session.commit()
        
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            return jsonify({
                'status': 'error',
                'message': 'Telegram credentials not configured. Please set Bot Token and Chat ID in settings.'
            }), 400
        
        # Initialize Telegram notifier
        if CONTROLLER_AVAILABLE:
            try:
                from src.telegram_notifier import TelegramNotifier
                
                notifier = TelegramNotifier(
                    bot_token=settings.telegram_bot_token,
                    chat_id=settings.telegram_chat_id
                )
                
                # Test message
                test_message = f"""
🤖 <b>WAR KRS Test Notification</b>

👤 <b>User:</b> {current_user.name}
✅ <b>Status:</b> Telegram integration working properly!

<i>This is a test message from WAR KRS automation system.</i>
                """
                
                success = notifier.send_message(test_message, parse_mode="HTML")
                
                if success:
                    log_activity(current_user.id, "Telegram test message sent successfully", "SUCCESS")
                    return jsonify({
                        'status': 'success',
                        'message': 'Test message sent successfully to Telegram!'
                    })
                else:
                    log_activity(current_user.id, "Failed to send Telegram test message", "ERROR")
                    return jsonify({
                        'status': 'error',
                        'message': 'Failed to send test message. Please check your Bot Token and Chat ID.'
                    }), 500
                    
            except ImportError:
                return jsonify({
                    'status': 'error',
                    'message': 'Telegram notification module not available'
                }), 500
        else:
            # Fallback using requests directly
            try:
                import requests
                from datetime import datetime
                
                url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
                
                test_message = f"""
🤖 WAR KRS Test Notification

👤 User: {current_user.name}
✅ Status: Telegram integration working properly!

This is a test message from WAR KRS automation system.
                """
                
                payload = {
                    'chat_id': settings.telegram_chat_id,
                    'text': test_message
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    log_activity(current_user.id, "Telegram test message sent successfully (fallback)", "SUCCESS")
                    return jsonify({
                        'status': 'success',
                        'message': 'Test message sent successfully to Telegram!'
                    })
                else:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('description', f'HTTP {response.status_code}')
                    log_activity(current_user.id, f"Failed to send Telegram test message: {error_msg}", "ERROR")
                    return jsonify({
                        'status': 'error',
                        'message': f'Failed to send test message: {error_msg}'
                    }), 500
                    
            except Exception as e:
                log_activity(current_user.id, f"Error in Telegram fallback: {str(e)}", "ERROR")
                return jsonify({
                    'status': 'error',
                    'message': f'Error sending test message: {str(e)}'
                }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }), 500

# Initialize database (called from run_web.py)
def init_db():
    """Initialize database tables"""
    db.create_all()
    
    # Try to migrate courses from GitHub if database is empty
    try:
        if Course.query.count() == 0:
            print("📚 No courses found in database, attempting migration from GitHub...")
            migrate_courses_from_md()
    except Exception as e:
        print(f"⚠️  Error during course migration: {e}")
    
    print("✅ Database initialized successfully")

if __name__ == '__main__':
    print("⚠️  Please use run_web.py to start the application")
    print("   python run_web.py")
    exit(1)
