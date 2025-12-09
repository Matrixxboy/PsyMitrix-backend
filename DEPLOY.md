# PsyMitrix Backend - Production Deployment Guide

This guide details the steps to deploy the PsyMitrix Backend to a shared Linux server (Ubuntu/Debian assumed). It is designed to allow this application to coexist safely with other applications running on the same server.

## 1. Deployment Summary

- **App Name**: `psymitrix-backend`
- **Python Version**: 3.10+
- **Port**: `8001` (Adjusted to avoid default 8000)
- **Database**: MySQL
- **Process Manager**: Systemd
- **Web Server**: Nginx (Reverse Proxy)
- **External Dependencies**: FFmpeg (Crucial for Audio/Video processing)

---

## 2. Prerequisites

Ensure the following are installed on the server:

- **Python 3.10+** and `pip`
- **Git**
- **MySQL Server**
- **FFmpeg** (Required for `pydub` and `whisper`)
- **Nginx**

### System Dependencies Installation
```bash
sudo apt update
sudo apt install python3-full python3-pip python3-venv ffmpeg -y
```

---

## 3. Project Setup

### 3.1. Clone/Upload Project
Navigate to your deployment directory (e.g., `/var/www/` or user home).

```bash
# Example: Deploying to /var/www/psymitrix
sudo mkdir -p /var/www/psymitrix
sudo chown -R $USER:$USER /var/www/psymitrix
# Upload your files here or clone via git
# cd /var/www/psymitrix
```

### 3.2. Directory Structure
Ensure your directory looks like this:
```
/var/www/psymitrix/
├── app/
│   ├── main.py
│   ├── services/
│   └── ...
├── generated_reports/  <-- Must be writable
├── public/             <-- Static assets
├── requirements.txt
├── .env                <-- Environment variables
└── venv/               <-- Virtual environment
```

### 3.3. Create Virtual Environment
Isolate dependencies to avoid conflicts with other apps.

```bash
cd /var/www/psymitrix
python3 -m venv venv
source venv/bin/activate
```

### 3.4. Install Python Dependencies
Your `requirements.txt` might be incomplete. Use the following comprehensive list to ensure all app features (FastAPI, MySQL, OpenAI, PDF generation) work.

**Recommended Installation Command:**
```bash
pip install "fastapi[standard]" uvicorn gunicorn python-multipart \
mysql-connector-python pydantic-settings openai \
pydub openai-whisper setuptools-rust reportlab pillow matplotlib numpy
```

---

## 4. Configuration

### 4.1. Environment Variables
Create a `.env` file in the root directory.

```bash
nano .env
```

**Paste the following (Update specific values):**
```ini
# Database
SQL_HOST=localhost
SQL_USER=your_db_user
SQL_PASSWORD=your_db_password
SQL_DATABASE=psybackend

# API Keys
OPEN_AI_API=sk-your-openai-key
GROQ_API=your-groq-key
OPENROUTER_API_KEY=your-openrouter-key
```

### 4.2. Verify Folders
Ensure the app can write to `generated_reports`:

```bash
mkdir -p generated_reports
chmod 755 generated_reports
```

---

## 5. Testing Manually

Before setting up the service, verify the app runs.

```bash
# From /var/www/psymitrix with venv activated
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

1. Check if it starts without errors.
2. Visit `http://your-server-ip:8001/docs` (if port is open) or `curl http://localhost:8001/health`.
3. Test audio/PDF generation.
4. **Ctrl+C** to stop.

---

## 6. Production Service (Systemd)

We will use **Systemd** to keep the app running and **Gunicorn** as a production-grade process manager with Uvicorn workers.

**Risk Mitigation**: We assign a specific port (8001) to avoid colliding with other apps on port 8000.

### 6.1. Create Service File
```bash
sudo nano /etc/systemd/system/psymitrix.service
```

### 6.2. Service Configuration
Paste this content. **Update User, Group, and paths.**

```ini
[Unit]
Description=PsyMitrix FastAPI Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/psymitrix
EnvironmentFile=/var/www/psymitrix/.env
ExecStart=/var/www/psymitrix/venv/bin/gunicorn -w 3 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8001 --timeout 120

# Restart automatically if it crashes
Restart=always

[Install]
WantedBy=multi-user.target
```
*Note: We bind to `127.0.0.1:8001` so it is NOT exposed to the public internet directly, only via Nginx.*

### 6.3. Start and Enable
```bash
sudo systemctl daemon-reload
sudo systemctl start psymitrix
sudo systemctl enable psymitrix
```

Check status:
```bash
sudo systemctl status psymitrix
```

---

## 7. Nginx Reverse Proxy

Configure Nginx to route traffic to your app. This allows you to host it alongside other apps (e.g., via a subdomain or subpath).

### Option A: Subdomain (Recommended)
`api.yourdomain.com`

### Option B: Subpath
`yourdomain.com/api`

### 7.1. Create Config
```bash
sudo nano /etc/nginx/sites-available/psymitrix
```

### 7.2. Configuration Content (Subdomain Example)
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeout for long requests (e.g. Whisper processing)
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
        
        # Allow large file uploads (Audio files)
        client_max_body_size 50M;
    }

    # Serve static files if needed
    location /public/ {
        alias /var/www/psymitrix/public/;
    }
}
```

### 7.3. Activate and Test
```bash
sudo ln -s /etc/nginx/sites-available/psymitrix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 8. Maintenance & Monitoring

### View Logs
```bash
# App logs (Systemd)
journalctl -u psymitrix -f

# Nginx logs
tail -f /var/log/nginx/error.log
```

### Restart Application
After code changes:
```bash
sudo systemctl restart psymitrix
```

### Update Deploy
```bash
cd /var/www/psymitrix
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # If new deps added
sudo systemctl restart psymitrix
```

## 9. Conflict Prevention on Shared Server

Since this is a shared server:
1.  **Port**: Do NOT use `8000`. We used `8001`. Keep a record of assigned ports.
2.  **Resources**: Heavy AI tasks (Whisper/PDF) can spike CPU.
    - If the server lags, reduce Gunicorn workers: `-w 1`.
3.  **Database**: Ensure `SQL_DATABASE` name (`psybackend`) is unique and doesn't conflict with other app DBs.
4.  **Static Files**: If Nginx is shared, ensure `server_name` is unique or `location` paths clearly separate apps.
