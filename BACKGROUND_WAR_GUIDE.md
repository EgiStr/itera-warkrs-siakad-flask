# Background WAR Processing untuk Vercel Serverless

Dokumentasi ini menjelaskan cara menjalankan WAR KRS secara background di Vercel menggunakan Cron Jobs dan Edge Functions.

## Mode Background yang Tersedia

### 1. Vercel Cron Mode (Recommended)
```python
# Setup WAR untuk dipanggil oleh Vercel Cron
result = run_war_process_serverless(user_id, session_id, app, db, mode="webhook")
```

### 2. Single Mode (Manual)
```python
# Sekali jalan saja
result = run_war_process_serverless(user_id, session_id, app, db, mode="single")
```

## Vercel Setup

### 1. Vercel Cron Configuration

Tambahkan di `vercel.json`:

```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 300
    }
  },
  "crons": [
    {
      "path": "/api/war/cron",
      "schedule": "*/5 8-17 * * 1-5"
    }
  ]
}
```

### 2. Environment Variables di Vercel

Set di Vercel Dashboard atau via CLI:

```bash
vercel env add WAR_CRON_SECRET
# Masukkan random string untuk security

vercel env add ENCRYPTION_KEY  
# Masukkan encryption key untuk cookies

vercel env add DATABASE_URL
# PostgreSQL connection string
```

## API Endpoints

### Start Background WAR (Vercel Cron)
```
POST /api/war/start-cron
Content-Type: application/json

{
    "user_id": 1,
    "interval_minutes": 5
}
```

### Cron Endpoint (Internal)
```
POST /api/war/cron
Content-Type: application/json
Authorization: Bearer VERCEL_CRON_SECRET

{
    "action": "process_all_active"
}
```

### Manual Trigger
```
POST /api/war/trigger
Content-Type: application/json

{
    "user_id": 1,
    "session_id": 123
}
```

### Check Status
```
GET /api/war/status/123
```

### Stop WAR
```
POST /api/war/stop/123
```

## Cara Penggunaan

### 1. Setup WAR Background via Web Interface

```javascript
// Start Vercel Cron WAR
fetch('/api/war/start-cron', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user_id: 1,
        interval_minutes: 5
    })
})
.then(response => response.json())
.then(data => {
    console.log('WAR started:', data);
    // Save session_id untuk monitoring
    const sessionId = data.session_id;
});
```

### 2. Manual Trigger

```javascript
// Trigger WAR manually
fetch('/api/war/trigger', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user_id: 1,
        session_id: 123  // Optional, will create if not provided
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### 3. Monitoring

```javascript
// Check status
fetch('/api/war/status/123')
.then(response => response.json())
.then(status => {
    console.log('Status:', status.status);
    console.log('Last activity:', status.last_activity);
    console.log('Courses obtained:', status.courses_obtained);
});

// Stop WAR
fetch('/api/war/stop/123', { method: 'POST' })
.then(response => response.json())
.then(data => console.log('Stopped:', data));
```

## Vercel Deployment

### 1. Update vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 300,
      "memory": 1024
    }
  },
  "crons": [
    {
      "path": "/api/war/cron",
      "schedule": "*/5 8-17 * * 1-5"
    }
  ],
  "env": {
    "VERCEL_ENV": "production"
  }
}
```

### 2. Environment Variables

```bash
# Via Vercel CLI
vercel env add WAR_CRON_SECRET
# Enter: your-secret-key-here

vercel env add ENCRYPTION_KEY
# Enter: your-encryption-key-here

vercel env add DATABASE_URL
# Enter: postgresql://user:pass@host:port/db

# Via Vercel Dashboard
# Go to Project Settings > Environment Variables
# Add the same variables
```

### 3. Deploy

```bash
# Deploy to Vercel
vercel --prod

# Check deployment
vercel ls

# View logs
vercel logs
```

## Monitoring

### Vercel Dashboard
- Monitor function executions
- View cron job logs  
- Check memory/duration usage
- Monitor error rates

### Application Logs
```javascript
// Get WAR session status with logs
fetch('/api/war/status/123')
.then(response => response.json())
.then(status => {
    console.log('Status:', status.status);
    console.log('Recent logs:', status.recent_logs);
});
```

### Telegram Notifications
Semua mode background mendukung notifikasi Telegram:
- Notifikasi start proses
- Notifikasi sukses per mata kuliah  
- Notifikasi completion
- Notifikasi error dan session expired

## Troubleshooting

### Common Issues

1. **Vercel Function Timeout**:
   - Default timeout 10 detik (Hobby plan)
   - Upgrade ke Pro plan untuk 60 detik
   - Atau gunakan cron dengan interval pendek

2. **Memory Limits**:
   - Default 1GB memory
   - Monitor usage di Vercel dashboard
   - Optimize import statements

3. **Cron Job Tidak Jalan**:
   - Check timezone (Vercel menggunakan UTC)
   - Verify cron syntax di vercel.json
   - Check function logs di dashboard

4. **Database Connection Issues**:
   - Use connection pooling
   - Set proper timeout values
   - Monitor connection count

5. **Session Expired**:
   - Update cookies di settings
   - WAR otomatis stop dan kirim notifikasi
   - Re-login dan update settings

## Performance & Limits

### Vercel Limits (Hobby Plan)
- Function timeout: 10 seconds
- Memory: 1024 MB
- Executions: 100GB-hours/month
- Cron jobs: 1 per project

### Vercel Pro Plan
- Function timeout: 60 seconds  
- Memory: up to 3008 MB
- Executions: 1000GB-hours/month
- Cron jobs: unlimited

### Optimization Tips
- Keep functions lightweight
- Use efficient database queries
- Implement proper error handling
- Monitor execution time
- Use caching where possible

## Security

### API Security
- Validate cron secret
- Sanitize input data
- Rate limiting on endpoints
- Monitor for abuse

### Data Security  
- Encrypt sensitive cookies ✅
- Use HTTPS only ✅
- Secure environment variables ✅
- Regular security updates

## Deployment Checklist

- [ ] Update vercel.json with cron configuration
- [ ] Set environment variables in Vercel
- [ ] Test cron endpoint manually
- [ ] Deploy with `vercel --prod`
- [ ] Monitor first cron execution
- [ ] Test Telegram notifications
- [ ] Verify WAR process works end-to-end
- [ ] Set up monitoring and alerts
