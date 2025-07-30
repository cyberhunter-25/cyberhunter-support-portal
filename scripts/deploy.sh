#!/bin/bash
# Deployment script for CyberHunter Security Portal

set -e  # Exit on error

echo "🚀 Deploying CyberHunter Security Portal..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo "❌ .env.production file not found!"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /var/www/cyberhunter-portal/uploads
mkdir -p /var/log/cyberhunter-portal
mkdir -p /etc/cyberhunter/ssl

# Set up SSL certificates
if [ ! -f /etc/cyberhunter/ssl/cert.pem ]; then
    echo "🔒 Setting up SSL certificates..."
    if [ "$USE_LETSENCRYPT" = "true" ]; then
        # Use Let's Encrypt
        apt-get install -y certbot
        certbot certonly --standalone -d $DOMAIN_NAME --non-interactive --agree-tos --email $ADMIN_EMAIL
        ln -sf /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem /etc/cyberhunter/ssl/cert.pem
        ln -sf /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem /etc/cyberhunter/ssl/key.pem
    else
        # Generate self-signed certificate for testing
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/cyberhunter/ssl/key.pem \
            -out /etc/cyberhunter/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=CyberHunter/CN=$DOMAIN_NAME"
    fi
fi

# Copy SSL certificates for Docker
cp /etc/cyberhunter/ssl/* docker/ssl/

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build and start containers
echo "🏗️  Building Docker images..."
docker-compose build --no-cache

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose run --rm web flask db upgrade

# Create initial admin user
echo "👤 Creating admin user..."
docker-compose run --rm web flask create-admin

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service status
echo "✅ Checking service status..."
docker-compose ps

# Set up cron jobs
echo "⏰ Setting up cron jobs..."
cat > /etc/cron.d/cyberhunter <<EOF
# CyberHunter Portal Cron Jobs
# Backup database daily at 2 AM
0 2 * * * root /usr/local/bin/docker-compose -f /opt/cyberhunter-portal/docker-compose.yml exec -T postgres pg_dump -U cyberhunter_user cyberhunter_portal | gzip > /var/backups/cyberhunter_\$(date +\%Y\%m\%d).sql.gz

# Clean old backups (keep 30 days)
0 3 * * * root find /var/backups -name "cyberhunter_*.sql.gz" -mtime +30 -delete

# Update ClamAV database
0 */6 * * * root /usr/local/bin/docker-compose -f /opt/cyberhunter-portal/docker-compose.yml exec -T web freshclam

# Let's Encrypt renewal
0 0 * * 0 root certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN_NAME/*.pem /opt/cyberhunter-portal/docker/ssl/ && docker-compose -f /opt/cyberhunter-portal/docker-compose.yml restart nginx
EOF

# Set up firewall
echo "🔥 Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Set up fail2ban
echo "🛡️  Setting up fail2ban..."
apt-get install -y fail2ban
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
EOF

systemctl restart fail2ban

# Final checks
echo "🔍 Running final checks..."
curl -k https://localhost/health || echo "⚠️  Health check failed"

echo "✅ Deployment complete!"
echo "🌐 Access the portal at: https://$DOMAIN_NAME"
echo "📧 Admin panel at: https://$DOMAIN_NAME/admin"
echo ""
echo "📝 Next steps:"
echo "1. Configure OAuth providers in Azure/Google Cloud"
echo "2. Update DNS records to point to this server"
echo "3. Test email configuration"
echo "4. Monitor logs: docker-compose logs -f"