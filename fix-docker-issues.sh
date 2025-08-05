#!/bin/bash

# Fix Docker and ClamAV issues
SERVER_IP="5.161.176.85"

ssh -t root@$SERVER_IP << 'ENDSSH'
cd /opt/cyberhunter-portal

echo "🔧 Fixing Docker configuration issues..."

# First, update the docker-compose.yml to remove nginx service (we're using system nginx)
cat > docker-compose-fixed.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: cyberhunter_portal
      POSTGRES_USER: cyberhunter_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cyberhunter_user -d cyberhunter_portal"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-changeme}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Flask Application
  web:
    build: .
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://cyberhunter_user:${DB_PASSWORD:-changeme}@postgres:5432/cyberhunter_portal
      REDIS_URL: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/0
      CELERY_BROKER_URL: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/1
      CELERY_RESULT_BACKEND: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/2
      FLASK_SECRET_KEY: ${FLASK_SECRET_KEY}
      MICROSOFT_CLIENT_ID: ${MICROSOFT_CLIENT_ID}
      MICROSOFT_CLIENT_SECRET: ${MICROSOFT_CLIENT_SECRET}
      GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
      GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET}
      SMTP_USERNAME: ${SMTP_USERNAME}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      IMAP_USERNAME: ${IMAP_USERNAME}
      IMAP_PASSWORD: ${IMAP_PASSWORD}
      DOMAIN_NAME: ${DOMAIN_NAME}
    volumes:
      - uploads:/var/www/cyberhunter-portal/uploads
      - logs:/var/log/cyberhunter-portal
    ports:
      - "127.0.0.1:5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker
  celery:
    build: .
    command: celery -A app.celery worker --loglevel=info
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://cyberhunter_user:${DB_PASSWORD:-changeme}@postgres:5432/cyberhunter_portal
      REDIS_URL: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/0
      CELERY_BROKER_URL: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/1
      CELERY_RESULT_BACKEND: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/2
    volumes:
      - uploads:/var/www/cyberhunter-portal/uploads
      - logs:/var/log/cyberhunter-portal
    depends_on:
      - postgres
      - redis

  # Celery Beat (Scheduler)
  celery-beat:
    build: .
    command: celery -A app.celery beat --loglevel=info
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://cyberhunter_user:${DB_PASSWORD:-changeme}@postgres:5432/cyberhunter_portal
      REDIS_URL: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/0
      CELERY_BROKER_URL: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/1
      CELERY_RESULT_BACKEND: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/2
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
  uploads:
  logs:
EOF

# Fix the freshclam configuration
cat > docker/freshclam.conf << 'EOF'
DatabaseDirectory /var/lib/clamav
UpdateLogFile /var/log/clamav/freshclam.log
Foreground true
DatabaseOwner clamav
Checks 24
MaxAttempts 5
DatabaseMirror database.clamav.net
EOF

# Fix the supervisord configuration to run as root initially
cat > docker/supervisord.conf << 'EOF'
[supervisord]
nodaemon=true

[program:freshclam]
command=/usr/bin/freshclam -d --quiet
autostart=false
autorestart=false
stdout_logfile=/var/log/supervisor/freshclam.log
stderr_logfile=/var/log/supervisor/freshclam.err

[program:clamd]
command=/usr/sbin/clamd --foreground=true
autostart=false
autorestart=false
stdout_logfile=/var/log/supervisor/clamd.log
stderr_logfile=/var/log/supervisor/clamd.err

[program:flask]
command=/usr/local/bin/gunicorn -b 0.0.0.0:5000 -w 4 --access-logfile - --error-logfile - run:app
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/flask.log
stderr_logfile=/var/log/supervisor/flask.err
environment=HOME="/app",USER="root"
EOF

# Create a simplified Dockerfile without ClamAV for now
cat > Dockerfile.simple << 'EOF'
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements/ /app/requirements/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /var/www/cyberhunter-portal/uploads \
    /var/log/cyberhunter-portal

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application directly with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
EOF

# Rebuild with simplified Dockerfile
echo "🔨 Rebuilding without ClamAV for now..."
docker-compose -f docker-compose-fixed.yml --env-file .env.production build --no-cache -f Dockerfile.simple

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose-fixed.yml --env-file .env.production up -d

# Wait and check
sleep 10
echo "📊 Checking status..."
docker-compose -f docker-compose-fixed.yml --env-file .env.production ps

# Update nginx to use correct port
echo "🔧 Updating Nginx configuration..."
cat > /etc/nginx/sites-available/guardian.clirsec.com << 'EOF'
server {
    listen 80;
    server_name guardian.clirsec.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name guardian.clirsec.com;

    ssl_certificate /etc/letsencrypt/live/guardian.clirsec.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/guardian.clirsec.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 16M;
}
EOF

nginx -t && systemctl reload nginx

echo "✅ Fixes applied!"
ENDSSH