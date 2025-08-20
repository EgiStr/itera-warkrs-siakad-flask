# Product Requirements Document (PRD): WAR KRS Web Platform

Dokumen ini menguraikan visi, fitur, dan persyaratan teknis untuk mentransformasikan tool warkrs dari aplikasi command-line (CLI) menjadi sebuah platform web yang aman, scalable, dan mudah digunakan.

---

## Versi

| Versi | Tanggal         | Author                | Status | Catatan                                               |
|-------|----------------|-----------------------|--------|-------------------------------------------------------|
| 1.0   | 20 Agustus 2025 | GitHub Copilot (CTO)  | Draft  | Inisiasi dokumen, Visi, MVP, dan Arsitektur           |
| 1.1   | 20 Agustus 2025 | GitHub Copilot (CTO)  | Draft  | Update ke Flask dengan Simple UI                      |

---

## 1. Visi & Latar Belakang

### 1.1 Masalah yang Ingin Diselesaikan

- **Hambatan Teknis:** Memerlukan pemahaman CLI, pip, .env, membatasi adopsi oleh mahasiswa non-teknis.
- **Manajemen Kredensial Rumit & Tidak Aman:** Pengguna harus menyalin CI_SESSION dan CF_CLEARANCE secara manual, berisiko kesalahan dan keamanan.
- **Tidak Scalable:** Setiap pengguna menjalankan instance sendiri, tanpa manajemen terpusat, monitoring, atau update mudah.
- **Pengalaman Pengguna Terbatas:** Interaksi berbasis teks kurang intuitif dibanding GUI.

### 1.2 Visi Produk

Menjadi platform "set-and-forget" yang aman dan andal bagi seluruh mahasiswa ITERA untuk mengotomatisasi pendaftaran KRS. Pengguna cukup login sekali, mengatur mata kuliah target melalui web, dan sistem bekerja otomatis di cloud dengan notifikasi real-time.

---

## 2. Tujuan & Metrik Keberhasilan (OKRs)

**Objective 1:** Meningkatkan Aksesibilitas & Adopsi Pengguna.
- KR1: 500+ pengguna aktif pada WAR KRS pertama.
- KR2: Onboarding time dari ~15 menit (CLI) menjadi < 3 menit (Web).
- KR3: Skor User Satisfaction (CSAT) > 8/10.

**Objective 2:** Meningkatkan Keamanan & Keandalan Sistem.
- KR1: Pengguna tidak perlu mengelola file .env/config.json manual.
- KR2: Uptime layanan > 99.5% selama periode krusial.
- KR3: Nol insiden keamanan terkait kredensial.

---

## 3. User Personas

| Persona | Deskripsi | Kebutuhan & Tujuan | Tantangan (CLI) |
|---------|-----------|--------------------|-----------------|
| Andi (Mahasiswa Non-Teknis) | Mahasiswa DKV, jarang pakai terminal | Cara mudah "memesan" mata kuliah, antarmuka simpel | Tidak familiar git/pip/python, setup membingungkan |
| Budi (Mahasiswa Teknik) | Mahasiswa Informatika, familiar CLI | Kontrol lebih, log real-time, script optimal | Copy-paste cookie manual merepotkan |
| Citra (Administrator) | Pengelola sistem | Monitor sistem, kelola pengguna, pastikan proses lancar | Tidak ada status pengguna terpusat |

---

## 4. Persyaratan Fungsional (MVP - Simple Flask Web App)

### 4.1 Manajemen Akun Pengguna (Sederhana)

- [P0] **User Login Simple:** Sistem login dasar menggunakan Flask-Login dengan session.
- [P0] **User Registration:** Form sederhana untuk daftar (NIM, Password, Nama).
- [P1] **Session Management:** Menggunakan Flask sessions, tidak perlu JWT untuk MVP.

### 4.2 Manajemen Sesi SIAKAD

- [P0] **Form Input Kredensial SIAKAD:** Halaman form untuk input NIM & Password SIAKAD.
- [P0] **Enkripsi Kredensial:** Simpan kredensial dengan enkripsi sederhana (Flask-Bcrypt).
- [P0] **Otomatisasi Cookie:** Backend Flask melakukan login otomatis ke SIAKAD untuk mendapatkan cookies.
- [P1] **Status Sesi:** Tampilkan status "Connected" atau "Disconnected" dari SIAKAD.

### 4.3 Dashboard Simple & Konfigurasi KRS

- [P0] **Dashboard Sederhana:** 
  - Status: Aktif/Stop/Error dalam card sederhana
  - Progress bar untuk menampilkan mata kuliah yang sudah didapat
- [P0] **Form Pemilihan Mata Kuliah:** 
  - Dropdown/Select untuk pilih mata kuliah dari list statis (COURSE_LIST.md)
  - Tambah/hapus mata kuliah dengan tombol sederhana
- [P0] **Tombol Start/Stop:** Button sederhana untuk mulai/hentikan proses
- [P0] **Log Sederhana:** Text area untuk menampilkan log terbaru (refresh manual)

### 4.4 Notifikasi Sederhana

- [P0] **Flash Messages:** Menggunakan Flask flash() untuk notifikasi sukses/error
- [P1] **Telegram (Optional):** Form untuk input Bot Token & Chat ID jika diperlukan

### 4.5 UI/UX Sederhana

- [P0] **Template Engine:** Jinja2 templates dengan CSS framework ringan (Bootstrap CDN)
- [P0] **Responsive Basic:** Layout yang responsive untuk mobile dan desktop
- [P0] **Navigation Simple:** Navbar sederhana dengan menu: Dashboard, Settings, Logout

---

## 5. Persyaratan Non-Fungsional

- **Keamanan:** HTTPS, proteksi CSRF/XSS/SQL Injection, enkripsi at-rest, rate limiting.
- **Skalabilitas:** Ratusan pengguna konkuren, background worker (Celery + Redis/RabbitMQ).
- **Performa:** Load halaman < 2 detik, backend non-blocking.
- **Keandalan:** Retry mekanisme, logging terpusat (ELK/Graylog).

---

## 6. Arsitektur Teknis (Flask Simple Web App)

### 6.1 Tech Stack Sederhana
- **Framework:** Flask (Python) dengan Jinja2 templates
- **Database:** SQLite (mudah deployment, cukup untuk MVP)
- **Authentication:** Flask-Login + Flask-Session
- **Forms:** WTForms untuk validasi form
- **Styling:** Bootstrap 5 CDN (tidak perlu build process)
- **Background Tasks:** Python Threading (sederhana, tidak perlu Redis/Celery)
- **Security:** Flask-Bcrypt untuk enkripsi password

### 6.2 Folder Structure
```
warkrs-web/
├── app.py                 # Main Flask application
├── models.py             # SQLite models dengan SQLAlchemy
├── forms.py              # WTForms untuk validasi
├── config.py             # Konfigurasi app
├── requirements.txt      # Dependencies
├── static/
│   ├── css/
│   │   └── custom.css    # CSS tambahan jika diperlukan
│   └── js/
│       └── main.js       # JavaScript minimal
├── templates/
│   ├── base.html         # Base template dengan Bootstrap
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── dashboard.html    # Main dashboard
│   ├── settings.html     # Settings page
│   └── logs.html         # Logs page
└── src/                  # KRS automation code (existing)
    ├── controller.py
    ├── parser.py
    └── telegram_notifier.py
```

### 6.3 Database
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nim VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- User settings table
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    siakad_nim VARCHAR(20),
    siakad_password_encrypted TEXT,
    telegram_bot_token TEXT,
    telegram_chat_id TEXT,
    target_courses TEXT, -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- WAR process tracking
CREATE TABLE war_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'stopped',
    started_at TIMESTAMP,
    stopped_at TIMESTAMP,
    courses_obtained TEXT, -- JSON string
    total_attempts INTEGER DEFAULT 0,
    successful_attempts INTEGER DEFAULT 0,
    last_activity TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Simple activity logs
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id INTEGER,
    level VARCHAR(10) DEFAULT 'INFO',
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (session_id) REFERENCES war_sessions (id)
);
```

### 6.4 Flask Routes
- `GET /` - Dashboard (status, progress, controls)
- `GET,POST /login` - Login form
- `GET,POST /register` - Registration form  
- `GET /logout` - Logout
- `GET,POST /settings` - Settings page
- `POST /war/start` - Start WAR process
- `POST /war/stop` - Stop WAR process
- `GET /logs` - View recent logs
- `GET /api/status` - AJAX endpoint untuk status updates

---

## 7. Rencana Implementasi & Roadmap

### 7.1 Fase 1: Flask MVP (2-3 Minggu)
**Week 1-2:**
- Setup Flask application dengan authentication dasar
- Buat database schema SQLite dan models
- Implement login/register dengan Flask-Login
- Create basic dashboard dengan status display

**Week 3:**
- Integrate existing KRS automation code (src/)
- Implement settings page untuk SIAKAD credentials & course selection
- Add background threading untuk WAR process
- Basic logging system

### 7.2 Fase 2: UI Enhancement (1 Minggu)
- Improve dashboard dengan progress indicators
- Add real-time status updates (AJAX polling)
- Implement Telegram notification configuration
- Add simple logs viewer page

### 7.3 Fase 3: Testing & Deployment (1 Minggu)
- Testing dengan SIAKAD environment
- Error handling improvements
- Simple deployment guide (Python + SQLite)
- Documentation untuk end users

### 7.4 Dependencies Minimal
```txt
Flask==2.3.3
Flask-Login==0.6.3
Flask-WTF==1.1.1
Flask-Bcrypt==1.0.1
Flask-SQLAlchemy==3.0.5
WTForms==3.0.1
requests==2.31.0
beautifulsoup4==4.12.2
cryptography==41.0.7
```

### 7.5 Deployment Simple
- **Development:** `python app.py` (Flask development server)
- **Production:** Gunicorn + Nginx (basic VPS deployment)
- **Database:** SQLite file (no external database required)
- **Static Files:** Served by Flask (simple deployment)

---

## 8. Risiko & Mitigasi

| Risiko | Tingkat | Mitigasi |
|--------|---------|----------|
| Perubahan Struktur HTML SIAKAD | Tinggi | Monitoring parser, notifikasi, update cepat |
| Pemblokiran IP oleh SIAKAD | Sedang | Proxy rotation, jitter pada request |
| Kebocoran Kredensial Pengguna | Kritis | Enkripsi end-to-end, audit keamanan, tidak log plain text |
| Ketergantungan pada Cookie | Tinggi | Riset login alternatif, panduan re-login manual |

---

> Dokumen ini adalah panduan utama pengembangan. Semua pemangku kepentingan diharapkan meninjau dan memberi masukan. Perubahan dikelola melalui kontrol versi terdokumentasi.

