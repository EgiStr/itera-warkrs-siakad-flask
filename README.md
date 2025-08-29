# 🚀 WAR KRS ITERA - Production Web Platform for Automated Course Registration

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.2.5-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0-red.svg)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5.3-green.svg)](https://docs.celeryproject.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Production](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)](https://krswar.hmsditera.com)
[![Security](https://img.shields.io/badge/security-enterprise%20grade-red.svg)](docs/SECURITY.md)

**🎯 Enterprise-grade web platform untuk otomatisasi pendaftaran KRS SIAKAD ITERA dengan arsitektur production-ready**

**🌐 Live Production:** [https://krswar.hmsditera.com](https://krswar.hmsditera.com)

[📋 Features](#-whats-new-in-production) • [🏗️ Architecture](#-production-architecture) • [🚀 Quick Start](#-quick-start) • [📖 Documentation](#-comprehensive-documentation) • [🔧 API Reference](#-api-reference)

</div>

---

## 🌟 What's New in Production

### 🎯 **Major Updates & Enhancements**

#### ✨ **Production Infrastructure (New!)**
- 🚀 **Full VPS Deployment** - Production server di `krswar.hmsditera.com`
- 🔧 **Nginx + Gunicorn** - High-performance WSGI server setup
- 📊 **Redis + Celery** - Distributed task queue untuk background processing
- 🗄️ **PostgreSQL Database** - Enterprise-grade database dengan Supabase
- 🔒 **SSL/HTTPS** - End-to-end encryption dengan Let's Encrypt
- 📈 **Auto-scaling** - Load balancing dan process management

#### 🛡️ **Enhanced Security & Reliability**
- 🔐 **Environment Isolation** - Proper `.env` configuration management
- 🚨 **Systemd Services** - Auto-restart dan monitoring services
- 📝 **Comprehensive Logging** - Production-grade logging system
- 🛡️ **Security Hardening** - Process isolation dan access controls
- 🔄 **Database Migrations** - Automated schema management
- ⚡ **Static File Optimization** - CDN-ready static assets serving

#### 🎨 **UI/UX Improvements**
- 📱 **Responsive Design** - Mobile-first responsive interface
- 🎯 **Real-time Updates** - Live status monitoring dashboard
- 🎨 **Modern UI** - Bootstrap 5 dengan custom styling
- 📊 **Advanced Analytics** - Detailed usage statistics
- 🔔 **Better Notifications** - Enhanced user feedback system

---

## 📚 Background & Motivation

### 🎓 **The Problem**
Mahasiswa Institut Teknologi Sumatera (ITERA) menghadapi tantangan signifikan dalam proses pendaftaran KRS:

- ⏰ **Time-Critical Registration** - Window pendaftaran KRS sangat terbatas
- 🏃‍♂️ **High Competition** - Ribuan mahasiswa compete untuk mata kuliah populer
- 🔄 **Manual Process** - Proses manual yang repetitif dan time-consuming
- 📱 **System Limitations** - SIAKAD sering overload saat jam sibuk
- 😰 **Stress Factor** - Tekanan psikologis untuk mendapatkan jadwal ideal

### 💡 **The Solution**
WAR KRS ITERA hadir sebagai solusi comprehensive yang mengatasi semua challenge di atas:

#### 🎯 **Core Philosophy**
- **Automation Over Manual** - Otomatisasi proses yang dapat diotomatisasi
- **Reliability Over Speed** - Sistem yang stabil dan dapat diandalkan
- **User Experience First** - Interface yang intuitif dan user-friendly
- **Security by Design** - Keamanan data mahasiswa sebagai prioritas utama
- **Scalability Ready** - Arsitektur yang dapat berkembang sesuai kebutuhan

#### 🌟 **Key Benefits**
- ⚡ **Efisiensi Waktu** - Menghemat 90%+ waktu pendaftaran KRS
- 🎯 **Success Rate Tinggi** - Algoritma optimized untuk maximize success rate
- 🛡️ **Data Protection** - Enkripsi end-to-end untuk credentials mahasiswa
- 📊 **Real-time Monitoring** - Transparent process tracking dan analytics
- 🤝 **Community Driven** - Open source dengan active community support

---

## 🏗️ Production Architecture

### 🔧 **Technology Stack**

#### **Backend Infrastructure**
```mermaid
graph TB
    subgraph "Production Server"
        A[Nginx Reverse Proxy] --> B[Gunicorn WSGI Server]
        B --> C[Flask Application]
        C --> D[SQLAlchemy ORM]
        D --> E[(PostgreSQL Database)]
        
        C --> F[Redis Cache]
        F --> G[Celery Workers]
        G --> H[Background Tasks]
    end
    
    subgraph "External Services"
        I[Supabase PostgreSQL]
        J[Telegram API]
        K[SIAKAD ITERA]
    end
    
    E -.-> I
    H --> J
    H --> K
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#ffebee
```

#### **🛠️ Core Technologies**

| Component | Technology | Version | Role |
|-----------|------------|---------|------|
| **Web Framework** | Flask | 2.2.5 | Core application framework |
| **WSGI Server** | Gunicorn | 23.0.0 | Production WSGI server |
| **Reverse Proxy** | Nginx | 1.22+ | Load balancer & static files |
| **Database** | PostgreSQL | 15+ | Primary data storage |
| **Cache & Queue** | Redis | 7.0+ | Caching & task queue broker |
| **Task Queue** | Celery | 5.3.4 | Background job processing |
| **ORM** | SQLAlchemy | 3.0.5 | Database abstraction |
| **Authentication** | Flask-Login | 0.6.2 | Session management |
| **Security** | Flask-Bcrypt | 1.0.1 | Password hashing |
| **Forms** | Flask-WTF | 1.1.1 | Form handling & CSRF |

#### **📊 Development & Production Stack**

```mermaid
graph LR
    subgraph "Development"
        A[Local SQLite] --> B[Flask Dev Server]
        B --> C[Hot Reload]
    end
    
    subgraph "Production"
        D[PostgreSQL] --> E[Gunicorn + Nginx]
        E --> F[SSL/HTTPS]
        F --> G[CDN Static Files]
    end
    
    subgraph "DevOps"
        H[Git Version Control]
        I[Environment Variables]
        J[Systemd Services]
        K[Log Monitoring]
    end
    
    style D fill:#e8f5e8
    style F fill:#fff3e0
    style J fill:#f3e5f5
```

---

## 🔄 Workflow & Process Flow

### 🎯 **Complete System Workflow**

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web Interface
    participant F as Flask App
    participant C as Celery Worker
    participant R as Redis Queue
    participant S as SIAKAD API
    participant T as Telegram Bot
    participant DB as Database

    Note over U,DB: Authentication Flow
    U->>W: Login Request
    W->>F: Validate Credentials
    F->>DB: Check User Data
    DB-->>F: User Verified
    F-->>W: Session Token
    W-->>U: Dashboard Access

    Note over U,DB: Course Management
    U->>W: Add/Import Courses
    W->>F: Process Course Data
    F->>DB: Store Course Info
    F->>C: Queue Background Validation
    C->>R: Task Queued
    C->>S: Validate Course Availability
    S-->>C: Course Status
    C->>DB: Update Course Status
    C->>T: Send Notification
    T-->>U: Course Update Alert

    Note over U,DB: WAR Execution
    U->>W: Start WAR Process
    W->>F: Initialize WAR
    F->>DB: Create WAR Session
    F->>C: Queue WAR Tasks
    C->>R: Multiple Tasks Queued
    
    loop For Each Course
        C->>S: Attempt Registration
        S-->>C: Registration Result
        C->>DB: Log Activity
        C->>T: Real-time Update
        T-->>U: Live Status
    end
    
    C->>DB: Final WAR Results
    C->>T: Completion Summary
    T-->>U: Final Report
```

### ⚡ **Background Task Processing**

```mermaid
flowchart LR
    subgraph "Main Process"
        A[Flask Web Server]
        B[Gunicorn Workers]
    end
    
    subgraph "Task Queue"
        C[Redis Broker]
        D[Task Queue]
    end
    
    subgraph "Background Workers"
        E[Celery Worker 1]
        F[Celery Worker 2]
        G[Celery Worker N]
    end
    
    subgraph "External APIs"
        H[SIAKAD ITERA]
        I[Telegram API]
    end
    
    subgraph "Data Store"
        J[(PostgreSQL)]
        K[Redis Cache]
    end
    
    A --> B
    B -->|Queue Tasks| C
    C --> D
    D --> E
    D --> F
    D --> G
    
    E -->|WAR Execution| H
    F -->|Send Notifications| I
    G -->|Data Processing| J
    
    E --> K
    F --> K
    G --> K
    
    style C fill:#ffcdd2
    style E fill:#c8e6c9
    style F fill:#c8e6c9
    style G fill:#c8e6c9
    style J fill:#bbdefb
```

### 🎮 **User Interaction Flow**

```mermaid
stateDiagram-v2
    [*] --> Login
    
    Login --> Dashboard : Success
    Login --> Login : Invalid Credentials
    
    Dashboard --> CourseManagement
    Dashboard --> Settings
    Dashboard --> WARExecution
    Dashboard --> ActivityLogs
    
    state CourseManagement {
        [*] --> ViewCourses
        ViewCourses --> AddCourse
        ViewCourses --> ImportCourses
        ViewCourses --> EditCourse
        AddCourse --> ViewCourses
        ImportCourses --> ViewCourses
        EditCourse --> ViewCourses
    }
    
    state Settings {
        [*] --> UserProfile
        UserProfile --> TelegramConfig
        TelegramConfig --> WarSettings
        WarSettings --> SaveSettings
        SaveSettings --> UserProfile
    }
    
    state WARExecution {
        [*] --> SelectCourses
        SelectCourses --> StartWAR
        StartWAR --> MonitorProgress
        MonitorProgress --> ViewResults
        ViewResults --> [*]
    }
    
    CourseManagement --> Dashboard
    Settings --> Dashboard
    WARExecution --> Dashboard
    ActivityLogs --> Dashboard
    
    Dashboard --> Logout
    Logout --> [*]
```

### 🔍 **Data Processing Pipeline**

```mermaid
flowchart TD
    subgraph "Input Layer"
        A[User Input]
        B[SIAKAD Data]
        C[Course Information]
    end
    
    subgraph "Processing Layer"
        D[Data Validation]
        E[Business Logic]
        F[Security Checks]
    end
    
    subgraph "Storage Layer"
        G[(User Data)]
        H[(Course Data)]
        I[(Activity Logs)]
        J[Redis Cache]
    end
    
    subgraph "Output Layer"
        K[Web Dashboard]
        L[Telegram Notifications]
        M[API Responses]
        N[Export Files]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    E --> F
    
    F --> G
    F --> H
    F --> I
    F --> J
    
    G --> K
    H --> K
    I --> L
    J --> M
    
    K --> N
    
    style D fill:#fff3e0
    style E fill:#e8f5e8
    style F fill:#ffebee
    style J fill:#f3e5f5
```

### 🔄 **Application Workflow**

#### **🔐 User Authentication Flow**
```mermaid
sequenceDiagram
    participant U as User
    participant W as Web App
    participant DB as Database
    participant S as Session Store
    
    U->>W: Access Login Page
    W->>U: Serve Login Form
    U->>W: Submit Credentials
    W->>DB: Validate User
    DB-->>W: User Data
    W->>S: Create Session
    S-->>W: Session Token
    W->>U: Redirect to Dashboard
    
    Note over U,S: Session persists across requests
```

#### **⚙️ Settings Configuration Flow**
```mermaid
sequenceDiagram
    participant U as User
    participant W as Web App
    participant E as Encryption
    participant DB as Database
    participant C as Course API
    
    U->>W: Access Settings
    W->>DB: Load User Settings
    W->>C: Fetch Available Courses
    C-->>W: Course List
    W->>U: Settings Form with Courses
    
    U->>W: Submit SIAKAD Cookies + Targets
    W->>E: Encrypt Sensitive Data
    E-->>W: Encrypted Cookies
    W->>DB: Save Encrypted Settings
    DB-->>W: Confirmation
    W->>U: Success Message
    
    Note over E: Fernet encryption for cookies
    Note over DB: Encrypted storage for security
```

#### **🎯 WAR Process Workflow**
```mermaid
sequenceDiagram
    participant U as User
    participant W as Web App
    participant R as Redis Queue
    participant C as Celery Worker
    participant S as SIAKAD
    participant T as Telegram
    participant DB as Database
    
    U->>W: Click Start WAR
    W->>DB: Create WAR Session
    W->>R: Queue Background Task
    R->>C: Dispatch Task to Worker
    
    loop WAR Automation Loop
        C->>DB: Load User Settings
        C->>S: Attempt Course Registration
        S-->>C: Registration Response
        
        alt Success
            C->>DB: Update Success Count
            C->>T: Send Success Notification
            C->>W: Update Dashboard Status
        else Failure
            C->>DB: Log Attempt
            C->>W: Update Dashboard Status
        end
        
        C->>C: Wait Cycle Delay
    end
    
    C->>DB: Final Session Update
    C->>T: Completion Notification
    C->>W: Process Complete
    
    Note over C,S: Retry logic with exponential backoff
    Note over T: Real-time notifications via Telegram
```

---

## 🚀 Production Deployment

### **📋 Prerequisites**
```bash
# System Requirements
- Ubuntu 22.04 LTS / CentOS 8+ / Debian 11+
- Python 3.10+ with pip
- PostgreSQL 14+ (or Supabase)
- Redis 7.0+
- Nginx 1.20+
- 1GB+ RAM recommended
- SSL Certificate (Let's Encrypt)
```

### **⚡ Quick Production Setup**

#### **1️⃣ System Dependencies**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python & development tools
sudo apt install python3.10 python3.10-venv python3-pip -y
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y

# Install PostgreSQL client (if using external DB)
sudo apt install postgresql-client -y

# Install Redis server
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install Nginx
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

#### **2️⃣ Application Setup**
```bash
# Clone and setup application
cd /home/wisata/
git clone https://github.com/your-repo/itera-warkrs-siakad-flask.git
cd itera-warkrs-siakad-flask

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn gevent psycopg2-binary python-dotenv

# Setup environment variables
cp .env.example .env
nano .env  # Edit with your configuration
```

#### **3️⃣ Database Initialization**
```bash
# Run database setup
source venv/bin/activate
python init_production_db.py

# Verify database connection
python -c "from app import app, db; app.app_context().push(); print('Database connected successfully')"
```

#### **4️⃣ Production Services**

**Gunicorn Configuration (`gunicorn_config.py`):**
```python
# Production-optimized Gunicorn configuration
import multiprocessing
import os

bind = "127.0.0.1:8000"
workers = 2  # Optimized for 1GB VPS
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 5

# Security & Performance
preload_app = True
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/home/wisata/itera-warkrs-siakad-flask/logs/gunicorn_access.log"
errorlog = "/home/wisata/itera-warkrs-siakad-flask/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "warkrs_gunicorn"
```

**Systemd Services Setup:**
```bash
# Create systemd services directory
sudo mkdir -p /etc/systemd/system

# Gunicorn service
sudo tee /etc/systemd/system/warkrs-gunicorn.service > /dev/null << 'EOF'
[Unit]
Description=Gunicorn instance to serve WARKRS Flask App
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=wisata
Group=www-data
WorkingDirectory=/home/wisata/itera-warkrs-siakad-flask
Environment=PATH=/home/wisata/itera-warkrs-siakad-flask/venv/bin
ExecStart=/home/wisata/itera-warkrs-siakad-flask/venv/bin/gunicorn -c gunicorn_config.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

# Celery worker service
sudo tee /etc/systemd/system/warkrs-celery-worker.service > /dev/null << 'EOF'
[Unit]
Description=Celery Worker for WARKRS Background Tasks
After=network.target redis.service

[Service]
Type=forking
User=wisata
Group=wisata
WorkingDirectory=/home/wisata/itera-warkrs-siakad-flask
Environment=PATH=/home/wisata/itera-warkrs-siakad-flask/venv/bin
ExecStart=/home/wisata/itera-warkrs-siakad-flask/venv/bin/celery -A celery_app worker --loglevel=info --logfile=/home/wisata/itera-warkrs-siakad-flask/logs/celery_worker.log --detach
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable warkrs-gunicorn warkrs-celery-worker
sudo systemctl start warkrs-gunicorn warkrs-celery-worker
```

#### **5️⃣ Nginx Configuration**
```nginx
# /etc/nginx/sites-available/krswar.hmsditera.com
server {
    listen 80;
    server_name krswar.hmsditera.com www.krswar.hmsditera.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name krswar.hmsditera.com www.krswar.hmsditera.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/krswar.hmsditera.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/krswar.hmsditera.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Static files optimization
    location /static/ {
        alias /home/wisata/itera-warkrs-siakad-flask/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
        
        location ~* \.(css|js)$ {
            add_header Content-Type text/plain;
            gzip on;
            gzip_vary on;
            gzip_types text/css application/javascript;
        }
    }
    
    # Media files
    location /media/ {
        alias /home/wisata/itera-warkrs-siakad-flask/media/;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket support (future enhancement)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    # Security: Block access to sensitive files
    location ~ /\.(ht|git|env) {
        deny all;
        return 404;
    }
    
    # Logs
    access_log /var/log/nginx/warkrs_access.log;
    error_log /var/log/nginx/warkrs_error.log warn;
}
```

#### **6️⃣ SSL Certificate Setup**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d krswar.hmsditera.com -d www.krswar.hmsditera.com

# Enable sites and restart services
sudo ln -sf /etc/nginx/sites-available/krswar.hmsditera.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### **🔧 Production Configuration**

#### **Environment Variables (`.env`):**
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
WTF_CSRF_SECRET_KEY=your-csrf-secret-key

# Database Configuration
DATABASE_URL=postgresql://username:password@host:5432/database
SQLALCHEMY_TRACK_MODIFICATIONS=false

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# Security Configuration
ENCRYPTION_KEY=your-fernet-encryption-key
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# External API Configuration
SIAKAD_BASE_URL=https://siakad.itera.ac.id
API_TIMEOUT=30
MAX_RETRY_ATTEMPTS=3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/home/wisata/itera-warkrs-siakad-flask/logs/app.log
```

#### **Redis Production Configuration:**
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Recommended settings for production:
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

### **📊 Monitoring & Maintenance**

#### **Health Checks:**
```bash
# Check service status
sudo systemctl status warkrs-gunicorn warkrs-celery-worker redis nginx

# Monitor logs
tail -f /home/wisata/itera-warkrs-siakad-flask/logs/gunicorn_error.log
tail -f /home/wisata/itera-warkrs-siakad-flask/logs/celery_worker.log
tail -f /var/log/nginx/warkrs_error.log

# Check Redis
redis-cli ping
redis-cli info memory

# Database health check
python -c "from app import app, db; app.app_context().push(); print(db.engine.execute('SELECT 1').scalar())"
```

#### **Performance Monitoring:**
```bash
# System resources
htop
df -h
free -m
iostat -x 1

# Application metrics
curl -s https://krswar.hmsditera.com/health | jq
redis-cli --latency-history
```

#### **Backup Strategy:**
```bash
# Database backup (if using PostgreSQL)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Application backup
tar -czf warkrs_backup_$(date +%Y%m%d).tar.gz \
  /home/wisata/itera-warkrs-siakad-flask \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude=logs \
  --exclude=*.pyc
```

---

## 📚 API Documentation

### **🔐 Authentication Endpoints**

#### **POST `/login`**
Authenticate user and create session.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "remember_me": "boolean"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "redirect_url": "/dashboard"
}
```

#### **POST `/register`**
Create new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "confirm_password": "string"
}
```

### **🎯 WAR Management Endpoints**

#### **POST `/start_war`**
Initiate WAR (automated registration) process.

**Headers:**
```
Content-Type: application/json
X-Requested-With: XMLHttpRequest
```

**Request Body:**
```json
{
  "course_ids": ["course1", "course2"],
  "settings": {
    "delay": 5000,
    "max_attempts": 100,
    "notify_telegram": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "war_session_id": "uuid-string",
  "message": "WAR process started successfully",
  "estimated_duration": "5-10 minutes"
}
```

#### **GET `/war_status/<session_id>`**
Get current status of WAR session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "running|completed|failed",
  "progress": {
    "total_courses": 5,
    "completed": 2,
    "success": 1,
    "failed": 1,
    "percentage": 40
  },
  "current_course": "Computer Networks",
  "last_update": "2024-01-15T10:30:00Z"
}
```

### **📚 Course Management Endpoints**

#### **GET `/api/courses`**
Retrieve user's courses with filtering and pagination.

**Query Parameters:**
```
?page=1&per_page=20&status=all&search=network
```

**Response:**
```json
{
  "courses": [
    {
      "id": "course_id",
      "course_code": "CS101",
      "course_name": "Computer Networks",
      "credits": 3,
      "semester": "2024/1",
      "status": "available|full|registered",
      "priority": 1,
      "last_checked": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 20,
    "total": 95
  }
}
```

#### **POST `/api/courses`**
Add new course to user's list.

**Request Body:**
```json
{
  "course_code": "CS101",
  "course_name": "Computer Networks",
  "credits": 3,
  "semester": "2024/1",
  "priority": 1
}
```

#### **PUT `/api/courses/<course_id>`**
Update course information.

**Request Body:**
```json
{
  "priority": 2,
  "enabled": false
}
```

#### **DELETE `/api/courses/<course_id>`**
Remove course from user's list.

### **⚙️ Settings Management**

#### **GET `/api/settings`**
Retrieve user settings.

**Response:**
```json
{
  "siakad_cookies": "encrypted_string",
  "telegram_chat_id": "123456789",
  "war_settings": {
    "delay_between_attempts": 5000,
    "max_retry_attempts": 100,
    "auto_stop_on_success": true,
    "notifications_enabled": true
  },
  "ui_preferences": {
    "theme": "dark",
    "language": "en",
    "dashboard_refresh_rate": 30
  }
}
```

#### **POST `/api/settings`**
Update user settings.

**Request Body:**
```json
{
  "siakad_cookies": "new_cookies_string",
  "telegram_chat_id": "987654321",
  "war_settings": {
    "delay_between_attempts": 3000,
    "max_retry_attempts": 150
  }
}
```

### **📊 Analytics & Logs**

#### **GET `/api/analytics`**
Get registration statistics and analytics.

**Response:**
```json
{
  "total_sessions": 25,
  "success_rate": 68.5,
  "most_successful_time": "07:00-09:00",
  "course_success_rates": [
    {
      "course_name": "Computer Networks",
      "attempts": 15,
      "successes": 12,
      "success_rate": 80.0
    }
  ],
  "weekly_stats": [
    {"week": "2024-W01", "attempts": 45, "successes": 28},
    {"week": "2024-W02", "attempts": 52, "successes": 35}
  ]
}
```

#### **GET `/api/activity_logs`**
Retrieve user activity logs with filtering.

**Query Parameters:**
```
?page=1&limit=50&level=info&start_date=2024-01-01&end_date=2024-01-31
```

**Response:**
```json
{
  "logs": [
    {
      "id": 123,
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "info|warning|error",
      "message": "Course registration attempt successful",
      "course_code": "CS101",
      "details": {
        "session_id": "uuid-string",
        "attempt_number": 5,
        "response_time": 1.23
      }
    }
  ],
  "pagination": {
    "page": 1,
    "total_pages": 10,
    "total_items": 487
  }
}
```

### **🔔 Webhook Endpoints**

#### **POST `/webhook/telegram`**
Telegram bot webhook for receiving updates.

**Request Body:** (Telegram Update format)
```json
{
  "update_id": 123456,
  "message": {
    "message_id": 789,
    "from": {
      "id": 987654321,
      "first_name": "User"
    },
    "chat": {
      "id": 987654321,
      "type": "private"
    },
    "date": 1642234567,
    "text": "/status"
  }
}
```

### **🛡️ Error Responses**

All endpoints follow consistent error response format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid course ID provided",
    "details": {
      "field": "course_id",
      "value": "invalid_id"
    }
  },
  "request_id": "req_123456789"
}
```

**Common Error Codes:**
- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_REQUIRED`: User not authenticated
- `AUTHORIZATION_DENIED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `EXTERNAL_SERVICE_ERROR`: SIAKAD or Telegram API error
- `INTERNAL_SERVER_ERROR`: Unexpected server error

---

## 📖 User Guide

### **🚀 Getting Started**

#### **1. Account Setup**
1. **Registration:**
   - Navigate to https://krswar.hmsditera.com/register
   - Fill in username, email, and secure password
   - Click "Create Account"
   - Verify email if required

2. **Initial Login:**
   - Go to https://krswar.hmsditera.com/login
   - Enter credentials
   - Check "Remember me" for convenience

3. **Dashboard Overview:**
   - View registration statistics
   - Monitor active WAR sessions
   - Quick access to all features

#### **2. SIAKAD Integration Setup**

1. **Obtain SIAKAD Cookies:**
   ```bash
   # Method 1: Browser Developer Tools
   1. Login to SIAKAD ITERA
   2. Open Developer Tools (F12)
   3. Go to Network tab
   4. Refresh page
   5. Find any request to siakad.itera.ac.id
   6. Copy 'Cookie' header value
   
   # Method 2: Browser Extension
   1. Install "Cookie Editor" extension
   2. Login to SIAKAD
   3. Open extension on siakad.itera.ac.id
   4. Export cookies as string
   ```

2. **Configure Settings:**
   - Navigate to "Settings" in dashboard
   - Paste SIAKAD cookies in designated field
   - Save configuration
   - Test connection using "Test Connection" button

#### **3. Course Management**

1. **Adding Courses:**
   - **Manual Entry:**
     - Click "Add Course" button
     - Fill course code, name, credits
     - Set priority (1 = highest)
     - Save course

   - **Bulk Import:**
     - Click "Import Courses"
     - Upload CSV file with format:
       ```csv
       course_code,course_name,credits,priority
       CS101,Computer Networks,3,1
       CS102,Data Structures,4,2
       ```
     - Review and confirm import

2. **Course Prioritization:**
   - Drag and drop to reorder
   - Higher priority = attempted first
   - Use priority 1-10 scale

3. **Course Status:**
   - 🟢 **Available**: Course has open slots
   - 🔴 **Full**: No available slots
   - ✅ **Registered**: Successfully registered
   - ⏸️ **Disabled**: Not included in WAR process

#### **4. WAR (Automated Registration) Process**

1. **Pre-WAR Checklist:**
   - ✅ SIAKAD cookies configured and tested
   - ✅ Courses added and prioritized
   - ✅ Telegram notifications configured (optional)
   - ✅ Stable internet connection
   - ✅ Check SIAKAD maintenance schedule

2. **Starting WAR:**
   - Go to dashboard
   - Review selected courses
   - Set WAR parameters:
     - **Delay**: Time between attempts (recommended: 3-5 seconds)
     - **Max Attempts**: Total retry limit (recommended: 50-100)
     - **Auto-stop**: Stop when target achieved
   - Click "Start WAR" button

3. **Monitoring Progress:**
   - Real-time progress bar
   - Live activity feed
   - Course-by-course status
   - Success/failure counters
   - Telegram notifications (if configured)

4. **Managing Active WAR:**
   - **Pause**: Temporarily halt process
   - **Resume**: Continue paused process
   - **Stop**: Terminate immediately
   - **Adjust Speed**: Modify delay dynamically

#### **5. Telegram Integration**

1. **Setup Bot:**
   ```bash
   # Create Telegram Bot
   1. Message @BotFather on Telegram
   2. Use /newbot command
   3. Follow instructions to get bot token
   4. Note down the token
   ```

2. **Get Chat ID:**
   ```bash
   # Method 1: Direct message bot
   1. Send any message to your bot
   2. Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
   3. Find "chat":{"id": YOUR_CHAT_ID}
   
   # Method 2: Use web interface
   1. Go to Settings → Telegram Integration
   2. Enter bot token
   3. Click "Get Chat ID"
   4. Follow instructions
   ```

3. **Configure Notifications:**
   - **Success Notifications**: Registration success alerts
   - **Failure Alerts**: Critical error notifications
   - **Progress Updates**: Periodic status reports
   - **Session Completion**: Final summary reports

4. **Telegram Commands:**
   - `/status` - Check current WAR status
   - `/stop` - Stop active WAR session
   - `/stats` - View registration statistics
   - `/help` - List available commands

### **🎯 Advanced Features**

#### **Multi-Session Management**
- Run multiple WAR sessions simultaneously
- Different course sets per session
- Session-specific settings
- Resource allocation controls

#### **Smart Scheduling**
- **Peak Hours Avoidance**: Automatically avoid high-traffic periods
- **Optimal Timing**: AI-suggested best registration times
- **Auto-retry**: Intelligent retry with exponential backoff
- **Cool-down Periods**: Prevent detection by spacing attempts

#### **Analytics Dashboard**
- **Success Rate Tracking**: Historical performance metrics
- **Time-based Analysis**: Best performing time slots
- **Course Popularity**: Success rates by course
- **Trend Analysis**: Weekly/monthly patterns
- **Comparative Statistics**: Personal vs. system averages

#### **Export & Reporting**
- **Activity Logs**: Detailed CSV export
- **Statistics Reports**: PDF generation
- **Course Lists**: Excel-compatible exports
- **Session History**: Complete audit trail

### **🛡️ Security Best Practices**

#### **Account Security**
1. **Strong Passwords:**
   - Minimum 12 characters
   - Mix of letters, numbers, symbols
   - Avoid dictionary words
   - Use password manager

2. **Session Management:**
   - Regular logout on shared devices
   - Monitor active sessions
   - Report suspicious activity

3. **Cookie Protection:**
   - Never share SIAKAD cookies
   - Regular cookie refresh
   - Use secure networks only

#### **SIAKAD Ethics**
1. **Respectful Usage:**
   - Reasonable delays between requests
   - Don't overwhelm servers
   - Respect rate limits

2. **Fair Play:**
   - Don't hoard course slots
   - Consider other students
   - Follow university policies

3. **Compliance:**
   - Adhere to ITERA's terms of service
   - Report system issues
   - Use for intended purposes only

### **🔧 Troubleshooting**

#### **Common Issues**

1. **"Invalid SIAKAD Cookies"**
   ```bash
   Solutions:
   - Re-login to SIAKAD and get fresh cookies
   - Check cookie format (should include all fields)
   - Ensure no extra spaces or line breaks
   - Verify SIAKAD session hasn't expired
   ```

2. **"WAR Process Stuck"**
   ```bash
   Causes & Solutions:
   - Network connectivity: Check internet connection
   - SIAKAD maintenance: Wait for system restoration
   - Rate limiting: Increase delay between attempts
   - Session timeout: Refresh SIAKAD cookies
   ```

3. **"Telegram Notifications Not Working"**
   ```bash
   Checklist:
   - Verify bot token is correct
   - Confirm chat ID is accurate
   - Check bot permissions
   - Test with /start command to bot
   ```

4. **"Courses Not Loading"**
   ```bash
   Troubleshooting:
   - Clear browser cache
   - Disable ad blockers
   - Check JavaScript enabled
   - Try incognito/private mode
   ```

#### **Performance Optimization**

1. **Slow Dashboard Loading:**
   - Clear browser cache
   - Disable unnecessary extensions
   - Check system resources
   - Use modern browser

2. **WAR Process Timing:**
   - Optimize delay settings (3-5 seconds recommended)
   - Avoid peak hours (7-9 AM, 12-2 PM)
   - Monitor system load
   - Use single course attempts during high load

#### **Contact & Support**

1. **Self-Help Resources:**
   - 📚 This documentation
   - 🎥 Video tutorials (if available)
   - 💬 Community forums
   - 📋 FAQ section

2. **Direct Support:**
   - 📧 Email: support@krswar.hmsditera.com
   - 🐛 Bug reports: GitHub Issues
   - 💡 Feature requests: GitHub Discussions
   - 🚨 Emergency: Telegram support bot

3. **Community:**
   - 💬 Telegram group: @warkrs_community
   - 🤝 Discord server: discord.gg/warkrs
   - 📱 WhatsApp group: (link in dashboard)

---

## 🤝 Contributing

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/your-repo/itera-warkrs-siakad-flask.git
cd itera-warkrs-siakad-flask

# Setup development environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v
```

### **Code Style & Standards**
- **Python**: Follow PEP 8, use `black` formatter
- **JavaScript**: ES6+, use `prettier` formatter
- **HTML/CSS**: Semantic markup, responsive design
- **Git**: Conventional commits format

### **Contributing Guidelines**
1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Ensure all tests pass: `pytest`
5. Commit changes: `git commit -m 'feat: add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Create Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### **Third-Party Licenses**
- **Flask**: BSD-3-Clause License
- **Celery**: BSD License
- **Redis**: BSD 3-Clause License
- **Bootstrap**: MIT License
- **Chart.js**: MIT License

---

## 🙏 Acknowledgments

- **Institut Teknologi Sumatera (ITERA)** - For the educational environment
- **Flask Community** - For the robust web framework
- **Celery Contributors** - For reliable background processing
- **Open Source Community** - For inspiration and contributions
- **Beta Testers** - For valuable feedback and bug reports
- **ITERA Students** - For feature requests and use cases

---

<div align="center">

### 🎯 **Ready to Automate Your Course Registration?**

**[🚀 Get Started Now](https://krswar.hmsditera.com/register) • [📚 Documentation](https://docs.krswar.hmsditera.com) • [💬 Community](https://t.me/warkrs_community) • [🐛 Report Issues](https://github.com/your-repo/issues)**

---

**Built with ❤️ for ITERA Students by ITERA Students**

*Last Updated: January 2024 - Version 2.1.0 Production*

</div>
```mermaid
graph TD
    A[HTML Templates] --> B[Bootstrap 5 UI]
    B --> C[Custom CSS/JS]
    C --> D[Responsive Design]
    D --> E[AJAX Real-time Updates]
    
    F[REST API Endpoints] --> G[JSON Responses]
    G --> H[Status Monitoring]
    H --> I[Real-time Logs]
    
    style A fill:#e3f2fd
    style F fill:#f1f8e9
```

#### **⚡ Business Logic Layer**
```mermaid
graph TD
    A[Flask Routes] --> B[Authentication]
    B --> C[Authorization]
    C --> D[Form Validation]
    D --> E[Business Rules]
    
    E --> F[WAR Controller]
    E --> G[Course Management]
    E --> H[User Management]
    E --> I[Settings Handler]
    
    style A fill:#fff3e0
    style F fill:#fce4ec
```

#### **💾 Data Access Layer**
```mermaid
graph TD
    A[SQLAlchemy Models] --> B[Database Abstraction]
    B --> C[Query Optimization]
    C --> D[Connection Pooling]
    D --> E[Transaction Management]
    
    F[Redis Cache] --> G[Session Storage]
    F --> H[Task Queue]
    F --> I[Performance Cache]
    
    style A fill:#e8f5e8
    style F fill:#ffebee
```

#### **🔧 Infrastructure Layer**
```mermaid
graph TD
    A[Nginx] --> B[Load Balancing]
    B --> C[SSL Termination]
    C --> D[Static File Serving]
    
    E[Gunicorn] --> F[Process Management]
    F --> G[Worker Scaling]
    
    H[Systemd] --> I[Service Management]
    I --> J[Auto Restart]
    J --> K[Log Management]
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style H fill:#fff8e1
```

---

## 🏗️ Architecture Overview

### 🎯 **Production Deployment Architecture**

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser] 
        B[Mobile App]
    end
    
    subgraph "CDN & Load Balancer"
        C[Cloudflare CDN]
        D[Nginx Load Balancer]
    end
    
    subgraph "Application Layer"
        E[Gunicorn Worker 1]
        F[Gunicorn Worker 2]
        G[Flask Application]
    end
    
    subgraph "Background Processing"
        H[Celery Worker Pool]
        I[Redis Task Queue]
        J[Background Tasks]
    end
    
    subgraph "Data Layer"
        K[PostgreSQL Primary]
        L[Redis Cache]
        M[Static Files Storage]
    end
    
    subgraph "External Services"
        N[SIAKAD ITERA API]
        O[Telegram Bot API]
        P[Supabase PostgreSQL]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    D --> F
    E --> G
    F --> G
    
    G --> H
    H --> I
    I --> J
    
    G --> K
    G --> L
    G --> M
    
    K -.-> P
    J --> N
    J --> O
    
    style C fill:#fff3e0
    style G fill:#e1f5fe
    style I fill:#ffebee
    style K fill:#e8f5e8
    style N fill:#f3e5f5
```

### 📁 Enhanced Project Structure

```
warkrsflask/ (Production Ready)
├── 🚀 Production Files
│   ├── app.py                        # Main Flask application (Enhanced)
│   ├── wsgi.py                       # WSGI entry point (New!)
│   ├── gunicorn_config.py            # Gunicorn configuration (New!)
│   ├── start_services.sh             # Service startup script (New!)
│   └── .env                          # Production environment variables
│
├── ⚙️ Configuration
│   ├── config_flask.py               # Multi-environment config
│   ├── nginx.conf                    # Nginx configuration (New!)
│   └── systemd/                      # System service files (New!)
│       ├── warkrs-gunicorn.service
│       ├── warkrs-celery-worker.service
│       └── warkrs-celery-beat.service
│
├── 🗄️ Database & Migrations
│   ├── warkrs.db                     # Development SQLite
│   ├── init_production_db.py         # Production DB setup
│   └── migrations/ (Future)          # Database migration files
│
├── 📊 Background Processing
│   ├── celery_app.py                 # Celery configuration (Enhanced)
│   ├── tasks/
│   │   ├── war_tasks.py              # Background WAR tasks
│   │   └── notification_tasks.py     # Telegram notifications
│   └── redis.conf                    # Redis configuration (New!)
│
├── 🌐 Web Interface
│   ├── templates/                    # Enhanced Jinja2 templates
│   │   ├── base.html                 # Responsive base template
│   │   ├── dashboard.html            # Real-time dashboard
│   │   ├── settings.html             # Enhanced settings
│   │   ├── courses.html              # Course management
│   │   ├── login.html                # Styled authentication
│   │   └── logs.html                 # Activity monitoring
│   │
│   └── static/                       # Production-optimized assets
│       ├── css/
│       │   ├── custom.css            # Enhanced styling
│       │   └── bootstrap.min.css     # Bootstrap 5
│       ├── js/
│       │   ├── main.js               # Enhanced JavaScript
│       │   ├── dashboard.js          # Real-time updates
│       │   └── chart.js              # Analytics charts
│       └── images/                   # Optimized images
│
├── 🔧 Business Logic (Enhanced)
│   └── src/
│       ├── controller.py             # Enhanced WAR controller
│       ├── krs_service.py            # SIAKAD service layer
│       ├── session.py                # HTTP session management
│       ├── telegram_notifier.py      # Telegram integration
│       ├── parser.py                 # HTML parsing utilities
│       ├── utils.py                  # Common utilities
│       └── security.py               # Security utilities (New!)
│
├── 📝 Logs & Monitoring
│   └── logs/
│       ├── app.log                   # Application logs
│       ├── gunicorn_access.log       # Access logs
│       ├── gunicorn_error.log        # Error logs
│       ├── celery_worker.log         # Worker logs
│       └── nginx_access.log          # Nginx logs
│
├── 🧪 Testing (Enhanced)
│   └── tests/
│       ├── test_auth.py              # Authentication tests
│       ├── test_war_controller.py    # WAR logic tests
│       ├── test_api.py               # API endpoint tests
│       ├── test_database.py          # Database tests
│       └── test_integration.py       # End-to-end tests
│
└── 📚 Documentation
    ├── README.md                     # This comprehensive guide
    ├── DEPLOYMENT.md                 # Production deployment guide
    ├── API_REFERENCE.md              # Complete API documentation
    ├── SECURITY.md                   # Security considerations
    └── CONTRIBUTING.md               # Contribution guidelines
```

---

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.12+** 
- **Git** untuk cloning repository
- **SIAKAD ITERA Account** dengan akses KRS
- **Telegram Bot** (optional, untuk notifikasi)

### ⚡ Installation & Setup

#### 1️⃣ Clone & Install Dependencies

```bash
# Clone repository
git clone <repository-url>
cd warkrsflask

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# atau .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2️⃣ Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```env
# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///warkrs.db

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

#### 3️⃣ Generate Security Keys

```bash
# Generate secure keys
python generate_keys.py

# Keys will be saved to deployment_keys.txt
cat deployment_keys.txt
```

#### 4️⃣ Initialize Database

```bash
# Initialize database and migrate courses
python init_production_db.py

# Start development server
python run_web.py

# Or using Flask CLI
flask run --debug --host=0.0.0.0 --port=5000
```

#### 5️⃣ Access Application

- **Local Development:** http://localhost:5000
- **Default Admin:** Create account melalui register page
- **Course Migration:** Otomatis dari `COURSE_LIST.md`

---

## 📖 User Guide

### 🔐 Authentication Flow

1. **Register Account** - Buat akun dengan NIM dan password
2. **Login** - Akses dashboard dengan credentials
3. **Setup Settings** - Konfigurasi cookies SIAKAD dan target courses
4. **Start WAR** - Mulai proses otomatisasi KRS

### ⚙️ Configuration Settings

#### 🍪 SIAKAD Cookies Setup

1. **Login ke SIAKAD ITERA** di browser
2. **Open Developer Tools** (F12)
3. **Go to Application/Storage tab**
4. **Copy Cookies:**
   - `CI_SESSION` - Session cookie SIAKAD
   - `CF_CLEARANCE` - Cloudflare clearance cookie
5. **Paste ke Settings page** di aplikasi

#### 📚 Course Selection

```json
{
  "target_courses": {
    "SD25-41301": "37813",    // Swarm Intelligence - R
    "IF25-40033": "35998",    // Tugas Akhir - R
    "TK25-40001": "36847",    // Perancangan Pabrik Kimia - RA
    "MA25-21302": "37636"     // Teori Graf - R
  }
}
```

**Course Format:** `"COURSE_CODE": "CLASS_ID"`

#### 🤖 Telegram Integration

1. **Create Bot:** Chat dengan @BotFather di Telegram
2. **Get Bot Token:** Simpan token dari BotFather
3. **Get Chat ID:** 
   - Send message ke bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Copy chat ID dari response
4. **Configure:** Input ke Settings page

### 🎛️ Dashboard Features

#### 📊 **Status Monitoring**
- **Session Status** - Active/Stopped/Error states
- **Statistics** - Total attempts, successful registrations
- **Course Progress** - Mata kuliah yang sudah didapat
- **Real-time Updates** - Auto-refresh status

#### 🎮 **Control Panel**
- **Start/Stop WAR** - Control automation process
- **Session Management** - Resume/restart capabilities
- **Emergency Stop** - Immediate halt functionality

#### 📝 **Activity Logs**
- **Detailed Logging** - Timestamped activities
- **Error Tracking** - Failed attempts dengan error details
- **Success Notifications** - Confirmed registrations
- **Export Logs** - Download activity history

---

## 🔧 API Reference

### 🌐 Web Routes

| Route | Method | Description | Auth Required |
|-------|--------|-------------|---------------|
| `/` | GET | Dashboard homepage | ✅ |
| `/login` | GET/POST | User authentication | ❌ |
| `/register` | GET/POST | Account registration | ❌ |
| `/logout` | POST | User logout | ✅ |
| `/settings` | GET/POST | User configuration | ✅ |
| `/courses` | GET | Course management | ✅ |
| `/courses/add` | GET/POST | Add new course | ✅ |
| `/courses/edit/<id>` | GET/POST | Edit course | ✅ |
| `/courses/delete/<id>` | POST | Delete course | ✅ |
| `/logs` | GET | Activity logs | ✅ |
| `/start-war` | POST | Start WAR process | ✅ |
| `/stop-war` | POST | Stop WAR process | ✅ |

### 📡 AJAX Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/status` | GET | Session status | JSON |
| `/api/logs/recent` | GET | Recent activity logs | JSON |
| `/api/courses/search` | GET | Search courses | JSON |
| `/api/telegram/test` | POST | Test Telegram connection | JSON |

### 📋 Request/Response Examples

#### Get Session Status
```bash
curl -X GET http://localhost:5000/api/status \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "status": "active",
  "total_attempts": 45,
  "successful_attempts": 2,
  "obtained_courses": ["SD25-41301", "MA25-21302"],
  "last_activity": "2025-08-20T10:30:00Z"
}
```

#### Start WAR Process
```bash
curl -X POST http://localhost:5000/start-war \
  -H "Cookie: session=..." \
  -H "X-CSRFToken: ..." \
  -d "csrf_token=..."
```

---

## 📊 Database Schema

### 👤 Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    nim VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### ⚙️ User Settings Table
```sql
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    ci_session TEXT,
    cf_clearance TEXT,
    telegram_bot_token TEXT,
    telegram_chat_id TEXT,
    target_courses TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 🎯 WAR Sessions Table
```sql
CREATE TABLE war_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'stopped',
    started_at TIMESTAMP,
    stopped_at TIMESTAMP,
    courses_obtained TEXT,  -- JSON
    total_attempts INTEGER DEFAULT 0,
    successful_attempts INTEGER DEFAULT 0,
    last_activity TIMESTAMP
);
```

### 📋 Courses Table
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL,
    course_name VARCHAR(200) NOT NULL,
    class_type VARCHAR(10),
    class_id VARCHAR(20) NOT NULL,
    faculty VARCHAR(100),
    department VARCHAR(100),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 📝 Activity Logs Table
```sql
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id INTEGER REFERENCES war_sessions(id),
    activity_type VARCHAR(50),
    message TEXT,
    details TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Deployment

### ☁️ Vercel Deployment

Aplikasi ini telah dikonfigurasi untuk deployment mudah ke **Vercel**:

#### 1️⃣ Prepare Deployment

```bash
# Run preparation script
bash prepare_vercel_deployment.sh

# Generate deployment keys
python generate_keys.py
```

#### 2️⃣ Setup Vercel Project

```bash
# Install Vercel CLI
npm i -g vercel

# Login dan setup project
vercel login
vercel

# Deploy
vercel --prod
```

#### 3️⃣ Environment Variables

Set di Vercel Dashboard atau CLI:

```bash
vercel env add FLASK_SECRET_KEY
vercel env add ENCRYPTION_KEY
vercel env add DATABASE_URL  # PostgreSQL untuk production
```

#### 4️⃣ Database Setup

**Recommended:** PostgreSQL di cloud service:

- **Supabase** (Free tier available)
- **Railway** (Free PostgreSQL)
- **Neon** (Serverless PostgreSQL)
- **AWS RDS** (Production scale)

### 🐳 Docker Deployment

```bash
# Build image
docker build -t warkrs-flask .

# Run container
docker run -d \
  --name warkrs-app \
  -p 5000:5000 \
  -e FLASK_SECRET_KEY=your_key \
  -e DATABASE_URL=your_db_url \
  warkrs-flask
```

### 🔧 Traditional VPS

```bash
# Setup production environment
python init_production_db.py

# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with Nginx + Gunicorn
# See docs/PRODUCTION_DEPLOYMENT.md
```

---

## 🛡️ Security Considerations

### 🔐 **Data Encryption**
- **Passwords** - bcrypt hashing dengan salt
- **Cookies** - Fernet symmetric encryption
- **Sensitive Data** - Database field encryption
- **Session Management** - Secure Flask sessions

### 🛡️ **Web Security**
- **CSRF Protection** - Flask-WTF tokens
- **SQL Injection** - SQLAlchemy ORM protection
- **XSS Prevention** - Jinja2 auto-escaping
- **Session Security** - HTTPOnly, Secure flags

### 🔒 **Authentication**
- **Password Policy** - Minimum 8 characters
- **Session Timeout** - Configurable expiry
- **Login Attempts** - Rate limiting (future)
- **Multi-factor** - Telegram verification (future)

### 📊 **Monitoring & Logging**
- **Activity Logs** - Comprehensive audit trail
- **Error Tracking** - Detailed error logging
- **Security Events** - Login attempts, failures
- **Performance Metrics** - Response times, usage stats

---

## 🧪 Testing

### 🔬 **Unit Tests**

```bash
# Run test suite
python -m pytest tests/

# Coverage report
python -m pytest --cov=app tests/

# Specific test categories
python -m pytest tests/test_auth.py
python -m pytest tests/test_war_controller.py
```

### 🌐 **Integration Tests**

```bash
# Test database operations
python -m pytest tests/test_database.py

# Test API endpoints
python -m pytest tests/test_api.py

# Test WAR functionality
python -m pytest tests/test_war_integration.py
```

### 🎭 **Load Testing**

```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:5000
```

---

## 🔧 Development

### 🛠️ **Local Development**

```bash
# Clone and setup
git clone <repo>
cd warkrsflask
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup pre-commit hooks
pip install pre-commit
pre-commit install

# Run development server
flask run --debug
```

### 📝 **Code Style**

```bash
# Format code
black app.py src/ tests/

# Check linting
flake8 app.py src/ tests/

# Type checking
mypy app.py src/
```

### 🗃️ **Database Migrations**

```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### 🐛 **Debugging**

```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Check logs
tail -f logs/app.log

# Database inspection
python -c "from app import db; db.create_all(); print('Tables created')"
```

---

## 📈 Performance & Monitoring

### 📊 **Metrics**

- **Response Time** - Average < 200ms for web pages
- **Database Queries** - Optimized with indexes
- **Memory Usage** - Lightweight SQLAlchemy models
- **Concurrent Users** - Supports 100+ simultaneous users

### 🔍 **Monitoring Tools**

- **Flask-SQLAlchemy** - Query monitoring
- **Activity Logs** - User behavior tracking
- **System Logs** - Application error logging
- **Vercel Analytics** - Production monitoring

### ⚡ **Optimization**

- **Database Indexing** - Optimized query performance
- **Static Assets** - CDN-ready static files
- **Background Tasks** - Async WAR processing
- **Connection Pooling** - Efficient database connections

---

## 🤝 Contributing

Kami sangat menyambut kontribusi dari komunitas! 

### 🚀 **Getting Started**

1. **Fork** repository ini
2. **Create feature branch** - `git checkout -b feature/amazing-feature`
3. **Commit changes** - `git commit -m 'Add amazing feature'`
4. **Push to branch** - `git push origin feature/amazing-feature`
5. **Open Pull Request**

### 📋 **Contribution Guidelines**

- ✅ **Code Style** - Follow PEP 8, use Black formatter
- ✅ **Testing** - Add tests untuk new features
- ✅ **Documentation** - Update docs untuk API changes
- ✅ **Security** - Follow security best practices
- ✅ **Performance** - Ensure efficient database queries

### 🐛 **Bug Reports**

Gunakan GitHub Issues dengan template:

```markdown
**Bug Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior:**
What you expected to happen

**Screenshots:**
If applicable, add screenshots

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.12.0]
- Flask: [e.g. 2.2.5]
```

### 💡 **Feature Requests**

```markdown
**Feature Description:**
Clear description of the feature

**Use Case:**
Why is this feature needed?

**Proposed Solution:**
How should this be implemented?

**Additional Context:**
Any other context or screenshots
```

---

## 📚 Additional Resources

### 📖 **Documentation**
- 📋 [Product Requirements Document](docs/PRD.MD)
- 🚀 [Deployment Guide](DEPLOYMENT_READY.md)
- 🔧 [Web Setup Instructions](WEB_SETUP.md)
- 🌐 [Vercel Deployment](VERCEL_DEPLOYMENT.md)

### 🔗 **Related Projects**
- [WAR KRS CLI](../README.md) - Original command-line version
- [SIAKAD Parser](src/parser.py) - HTML parsing utilities
- [Telegram Bot Integration](src/telegram_notifier.py)

### 🎓 **Learning Resources**
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.1/)
- [Vercel Functions](https://vercel.com/docs/functions)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### ⚠️ Disclaimer

Tool ini dibuat untuk tujuan **edukasi** dan membantu mahasiswa ITERA dalam proses pendaftaran KRS. 

**Important Notes:**
- ✅ Gunakan dengan **bijak** dan ikuti kebijakan institusi
- ✅ **Respect** terms of service SIAKAD ITERA  
- ✅ **Testing** dilakukan di environment yang controlled
- ✅ **Tidak bertanggung jawab** atas penyalahgunaan tool

---

## 🙏 Acknowledgments

- **Institut Teknologi Sumatera** - Untuk SIAKAD system yang robust
- **Flask Community** - Untuk framework yang excellent
- **Python Community** - Untuk ecosystem yang amazing
- **Contributors** - Yang telah membantu development

---

## 📞 Support & Contact

- 🐛 **Bug Reports:** [GitHub Issues](../../issues)
- 💡 **Feature Requests:** [GitHub Discussions](../../discussions)
- 📧 **Email:** your-email@domain.com
- 💬 **Telegram:** @your_telegram

---

<div align="center">

**⭐ Jika project ini membantu, jangan lupa kasih star!**

Made with ❤️ by the WAR KRS Team

</div>
