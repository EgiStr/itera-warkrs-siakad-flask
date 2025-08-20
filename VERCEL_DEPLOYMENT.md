# Deployment WAR KRS Flask ke Vercel

Panduan ini menjelaskan cara melakukan deploy aplikasi WAR KRS Flask ke platform Vercel.

## Persyaratan

1. Akun Vercel (gratis di [vercel.com](https://vercel.com))
2. Git repository (GitHub, GitLab, atau Bitbucket)
3. Vercel CLI (opsional, untuk deployment lokal)

## Langkah-langkah Deployment

### 1. Persiapan Environment Variables

Sebelum deploy, Anda perlu menyiapkan environment variables berikut di dashboard Vercel:

#### Environment Variables Wajib:
- `FLASK_SECRET_KEY`: Key rahasia untuk Flask session (generate key yang kuat)
- `ENCRYPTION_KEY`: Key untuk enkripsi password SIAKAD (gunakan Fernet key)
- `DATABASE_URL`: URL database (untuk production, gunakan PostgreSQL atau MySQL cloud)

#### Environment Variables Opsional:
- `FLASK_CONFIG`: Set ke `production` (default sudah diset di vercel.json)

### 2. Generate Encryption Key

Untuk generate encryption key, jalankan Python script berikut:

```python
from cryptography.fernet import Fernet
print(f"ENCRYPTION_KEY={Fernet.generate_key().decode()}")
```

### 3. Setup Database External (Rekomendasi untuk Production)

Karena Vercel functions adalah serverless dan tidak menyimpan data permanen, disarankan menggunakan database external seperti:

- **PostgreSQL**: Railway, Supabase, atau Neon
- **MySQL**: PlanetScale atau AWS RDS
- **SQLite Cloud**: Turso

Contoh setup PostgreSQL dengan Supabase:
1. Buat project di [supabase.com](https://supabase.com)
2. Dapatkan connection string PostgreSQL
3. Set sebagai `DATABASE_URL` di Vercel

### 4. Deploy via GitHub

#### Metode 1: Auto-deploy dari GitHub

1. Push kode ke repository GitHub
2. Masuk ke [vercel.com](https://vercel.com)
3. Klik "New Project"
4. Import repository GitHub Anda
5. Vercel akan otomatis mendeteksi file `vercel.json`
6. Set environment variables di project settings
7. Deploy!

#### Metode 2: Manual deploy dengan Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login ke Vercel
vercel login

# Deploy dari direktori project
cd /path/to/warkrsflask
vercel

# Untuk production deployment
vercel --prod
```

### 5. Set Environment Variables di Vercel Dashboard

1. Masuk ke dashboard Vercel
2. Pilih project Anda
3. Masuk ke Settings > Environment Variables
4. Tambahkan variable berikut:

```
FLASK_SECRET_KEY=your-super-secret-key-here
ENCRYPTION_KEY=your-fernet-encryption-key-here
DATABASE_URL=postgresql://user:password@host:port/database
```

### 6. Testing Deployment

Setelah deployment selesai, test aplikasi:

1. Buka URL yang diberikan Vercel
2. Coba registrasi user baru
3. Test login/logout
4. Test pengaturan cookies SIAKAD
5. Test fitur WAR KRS (jika sudah ada data courses)

## Struktur File untuk Vercel

```
warkrsflask/
├── api/
│   └── index.py          # Entry point Vercel
├── src/                  # Business logic
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── vercel.json          # Konfigurasi Vercel
├── requirements.txt     # Python dependencies
├── Pipfile             # Python version specification
├── .vercelignore       # Files to ignore during build
└── .env.example        # Template environment variables
```

## Troubleshooting

### Error: Module not found
- Pastikan semua dependencies ada di `requirements.txt`
- Check Python path configuration di `api/index.py`

### Database connection error
- Pastikan `DATABASE_URL` sudah di-set dengan benar
- Test koneksi database secara terpisah
- Untuk SQLite, database akan disimpan di `/tmp` (tidak persistent)

### Timeout errors
- Vercel functions memiliki timeout limit (10 detik untuk free plan)
- Optimize database queries
- Pertimbangkan menggunakan background jobs untuk proses yang lama

### Static files tidak load
- Pastikan path static files benar di templates
- Check konfigurasi static folder di Flask app

## Monitoring dan Logs

1. **Vercel Dashboard**: Real-time logs dan metrics
2. **Function Logs**: Check logs di Vercel dashboard untuk debugging
3. **Performance**: Monitor response time dan usage

## Security Considerations

1. **Environment Variables**: Jangan commit secrets ke git
2. **HTTPS**: Vercel otomatis menyediakan HTTPS
3. **CSRF Protection**: Sudah enabled di Flask-WTF
4. **Database Security**: Gunakan SSL connection untuk database

## Limitations di Vercel

1. **Stateless**: Setiap request adalah function call terpisah
2. **No Background Tasks**: Tidak bisa menjalankan background processes
3. **File Storage**: Tidak ada persistent file storage
4. **Execution Time**: Limited execution time per function

## Alternative Deployment

Jika WAR KRS membutuhkan background processing yang long-running, pertimbangkan platform lain:

- **Railway**: Supports long-running processes
- **Heroku**: Traditional PaaS with worker dynos
- **DigitalOcean App Platform**: Container-based deployment
- **AWS/GCP**: More control over infrastructure

## Support

Jika mengalami issues, check:
1. Vercel function logs
2. Database connection
3. Environment variables configuration
4. Python dependencies compatibility
