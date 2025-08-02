# CyberHunter Security Portal - Deployment Guide

This guide walks through deploying the CyberHunter Security Portal to a cloud server.

## Prerequisites

- A cloud server (Ubuntu 22.04 LTS recommended)
- Domain name pointed to your server
- SSH access to the server
- Basic knowledge of Docker and Linux commands

## Quick Start Deployment

1. **Clone the repository on your server**
   ```bash
   git clone https://github.com/cyberhunter-25/cyberhunter-support-portal.git
   cd cyberhunter-support-portal
   ```

2. **Configure environment variables**
   ```bash
   cp .env.production.example .env.production
   nano .env.production
   ```

3. **Run the deployment script**
   ```bash
   sudo ./scripts/deploy.sh
   ```

This automated script will:
- Install Docker and Docker Compose
- Set up SSL certificates
- Configure the firewall
- Deploy all services
- Create the initial admin user

## Manual Deployment Steps

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git curl wget ufw fail2ban

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 2. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)
```bash
sudo apt install certbot
sudo certbot certonly --standalone -d support.yourdomain.com
```

#### Option B: Self-Signed (Testing only)
```bash
mkdir -p docker/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/key.pem \
  -out docker/ssl/cert.pem
```

### 4. Configure Environment

Create `.env.production` with your settings:

```bash
# Required Settings
DOMAIN_NAME=support.yourdomain.com
FLASK_SECRET_KEY=your-very-long-random-secret-key
DB_PASSWORD=secure-database-password
REDIS_PASSWORD=secure-redis-password

# OAuth Configuration
MICROSOFT_CLIENT_ID=your-azure-app-id
MICROSOFT_CLIENT_SECRET=your-azure-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret

# Email Settings
SMTP_USERNAME=guardian@clirsec.com
SMTP_PASSWORD=gmail-app-password
IMAP_USERNAME=guardian@clirsec.com
IMAP_PASSWORD=gmail-app-password
```

### 5. Deploy the Application

```bash
# Build and start services
docker-compose --env-file .env.production up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 6. Initialize Database

```bash
# Run migrations
docker-compose exec web flask db upgrade

# Create admin user
docker-compose exec web flask create-admin
```

## OAuth Provider Setup

### Microsoft Azure

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "App registrations"
3. Click "New registration"
4. Configure:
   - Name: CyberHunter Support Portal
   - Supported account types: Accounts in any organizational directory
   - Redirect URI: `https://support.yourdomain.com/auth/callback/microsoft`
5. Save the Application (client) ID
6. Create a client secret under "Certificates & secrets"

### Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Configure:
   - Authorized redirect URIs: `https://support.yourdomain.com/auth/callback/google`
6. Save the client ID and secret

## Post-Deployment

### 1. Create Test Company

```bash
docker-compose exec web flask create-test-company
```

### 2. Configure Email

For Gmail:
1. Enable 2-factor authentication
2. Generate app-specific password
3. Use app password in `.env.production`

### 3. Set Up Monitoring

```bash
# Check application health
curl https://support.yourdomain.com/health

# Monitor logs
docker-compose logs -f web

# Check disk usage
df -h

# Monitor system resources
htop
```

### 4. Configure Backups

The deployment script sets up automatic backups. Verify with:
```bash
sudo crontab -l
```

### 5. Security Hardening

```bash
# Check fail2ban status
sudo fail2ban-client status

# Review nginx logs
docker-compose logs nginx

# Check SSL configuration
curl -I https://support.yourdomain.com
```

## Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Backup

```bash
# Manual backup
docker-compose exec postgres pg_dump -U cyberhunter_user cyberhunter_portal | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore backup
gunzip < backup_20250730.sql.gz | docker-compose exec -T postgres psql -U cyberhunter_user cyberhunter_portal
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 80
sudo lsof -i :80
# Kill process if needed
sudo kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U cyberhunter_user -d cyberhunter_portal
```

### Email Not Working
```bash
# Test SMTP connection
docker-compose exec web python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.extensions import mail; mail.send_message(subject='Test', recipients=['test@example.com'], body='Test email')"
```

### SSL Certificate Issues
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Copy renewed certificates
sudo cp /etc/letsencrypt/live/support.yourdomain.com/*.pem docker/ssl/
docker-compose restart nginx
```

## Performance Optimization

### Enable Redis Caching
Already configured in the application

### Configure Nginx Caching
Edit `docker/nginx.conf` to add caching headers

### Database Optimization
```bash
# Analyze database
docker-compose exec postgres psql -U cyberhunter_user -d cyberhunter_portal -c "ANALYZE;"

# Check slow queries
docker-compose exec postgres psql -U cyberhunter_user -d cyberhunter_portal -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## Scaling

### Horizontal Scaling
1. Set up a load balancer
2. Deploy multiple web containers
3. Use shared Redis for sessions
4. Use shared file storage for uploads

### Vertical Scaling
Upgrade your server resources as needed

## Support

For deployment issues:
- Check logs: `docker-compose logs`
- Review this guide
- Contact CyberHunter support

## Security Checklist

- [ ] SSL certificate installed and working
- [ ] Firewall configured (only ports 22, 80, 443 open)
- [ ] fail2ban active
- [ ] Strong passwords for all services
- [ ] OAuth providers configured correctly
- [ ] Email credentials secure
- [ ] Backups configured and tested
- [ ] Monitoring active
- [ ] Regular security updates scheduled