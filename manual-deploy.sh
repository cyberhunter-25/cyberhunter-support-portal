#!/bin/bash

# Manual deployment script with fixes

SERVER_IP="5.161.176.85"
SERVER_USER="root"

echo "🔧 Manual CyberHunter Portal Deployment"
echo "======================================"
echo ""

# First, let's fix the GitHub SSH host key issue and deploy manually
ssh -t $SERVER_USER@$SERVER_IP << 'ENDSSH'

echo "📂 Setting up deployment..."

# Add GitHub to known hosts
echo "🔑 Adding GitHub to known hosts..."
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts 2>/dev/null

# Create app directory
mkdir -p /opt/cyberhunter-portal
cd /opt/cyberhunter-portal

# Remove any failed clone attempts
rm -rf .git

# Try cloning (public HTTPS method)
echo "📥 Cloning repository (HTTPS)..."
if git clone https://github.com/cyberhunter-25/cyberhunter-support-portal.git .; then
    echo "✅ Repository cloned successfully"
else
    echo "❌ HTTPS clone failed. Repository might be private."
    echo ""
    echo "Trying SSH method..."
    
    # Test GitHub SSH connection
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ GitHub SSH authentication working"
        git clone git@github.com:cyberhunter-25/cyberhunter-support-portal.git .
    else
        echo "❌ GitHub SSH not configured properly"
        echo ""
        echo "Please either:"
        echo "1. Make the repository public at:"
        echo "   https://github.com/cyberhunter-25/cyberhunter-support-portal/settings"
        echo ""
        echo "2. Or ensure the server's SSH key is added to GitHub"
        exit 1
    fi
fi

# If we got here, clone succeeded
if [ -f "docker-compose.yml" ]; then
    echo ""
    echo "✅ Repository cloned successfully!"
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        echo ""
        echo "🐳 Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl start docker
        systemctl enable docker
        rm get-docker.sh
        
        # Install Docker Compose
        echo "📦 Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    else
        echo "✅ Docker is already installed"
    fi
    
    # Create production environment file
    if [ ! -f .env.production ]; then
        echo ""
        echo "📝 Creating production environment template..."
        
        # Create a basic .env.production file
        cat > .env.production << 'EOF'
# CyberHunter Portal Production Configuration
# IMPORTANT: Update all values below!

# Basic Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=change-this-to-a-very-long-random-string

# Domain Configuration
DOMAIN_NAME=your-domain.com
SERVER_NAME=your-domain.com

# Database Configuration
DATABASE_URL=postgresql://cyberhunter_user:change-this-password@postgres:5432/cyberhunter_portal
DB_PASSWORD=change-this-password

# Redis Configuration
REDIS_URL=redis://:change-this-password@redis:6379/0
REDIS_PASSWORD=change-this-password

# OAuth Configuration - Microsoft
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# OAuth Configuration - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=guardian@clirsec.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_USE_TLS=True

IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=guardian@clirsec.com
IMAP_PASSWORD=your-gmail-app-password

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Celery Configuration
CELERY_BROKER_URL=redis://:change-this-password@redis:6379/0
CELERY_RESULT_BACKEND=redis://:change-this-password@redis:6379/0

# Push Notifications (optional)
NTFY_TOPIC=cyberhunter-alerts
NTFY_SERVER=https://ntfy.sh
EOF
        
        echo "✅ Created .env.production template"
        echo ""
        echo "⚠️  IMPORTANT: You must edit .env.production with your actual values!"
    fi
    
    # Build and start services
    echo ""
    echo "🔨 Building Docker containers..."
    docker-compose -f docker-compose.yml --env-file .env.production build --no-cache
    
    echo ""
    echo "🚀 Starting services..."
    docker-compose -f docker-compose.yml --env-file .env.production up -d
    
    # Wait for services
    echo ""
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Show status
    echo ""
    echo "📊 Service status:"
    docker-compose -f docker-compose.yml --env-file .env.production ps
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit /opt/cyberhunter-portal/.env.production with your actual values"
    echo "2. Run: docker-compose restart"
    echo "3. Set up SSL certificate for your domain"
    echo "4. Create admin user: docker-compose exec web flask create-admin"
else
    echo "❌ Failed to clone repository"
fi

ENDSSH

echo ""
echo "🏁 Deployment script finished!"