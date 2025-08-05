#!/bin/bash

# Deployment script for CyberHunter Support Portal
# This script handles the deployment with password-protected SSH keys

SERVER_IP="5.161.176.85"
SERVER_USER="root"
APP_DIR="/opt/cyberhunter-portal"

echo "🚀 CyberHunter Support Portal Deployment"
echo "========================================"
echo "Server: $SERVER_USER@$SERVER_IP"
echo ""
echo "You will be prompted for your SSH key password when connecting."
echo ""

# Function to execute commands on server
remote_exec() {
    ssh -i /Users/cdodunski/.ssh/claude_code_key $SERVER_USER@$SERVER_IP "$@"
}

# Step 1: Test connection
echo "📡 Testing connection..."
if remote_exec "echo 'Connection successful!'"; then
    echo "✅ Connected to server"
else
    echo "❌ Failed to connect. Please check your SSH key password."
    exit 1
fi

# Step 2: Push local changes to GitHub first
echo ""
echo "📤 Pushing local changes to GitHub..."
git add .
git commit -m "Deploy to production" -m "🤖 Auto-commit before deployment" || echo "No changes to commit"
git push origin main || echo "Push failed - continuing anyway"

# Step 3: Deploy on server
echo ""
echo "🔧 Starting deployment on server..."

remote_exec << 'ENDSSH'
set -e

echo "📂 Setting up application directory..."
mkdir -p /opt/cyberhunter-portal
cd /opt/cyberhunter-portal

# Clone or update repository
if [ -d ".git" ]; then
    echo "📥 Stashing existing changes, removing untracked files, and pulling latest..."
    git stash
    git clean -fd
    git pull origin main
else
    echo "📥 Cloning repository..."
    # Try SSH clone first, fall back to HTTPS if needed
    git clone git@github.com:cyberhunter-25/cyberhunter-support-portal.git . || \
    git clone https://github.com/cyberhunter-25/cyberhunter-support-portal.git .
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
    
    # Install Docker Compose
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create production environment file if it doesn't exist
if [ ! -f .env.production ]; then
    echo "📝 Creating production environment file..."
    cp .env.production.example .env.production || cp .env.example .env.production || true
    echo ""
    echo "⚠️  IMPORTANT: Edit .env.production with your actual values!"
    echo "   Especially: OAuth credentials, email settings, and domain name"
fi

# Build and deploy
echo ""
echo "🔨 Building and deploying application..."
docker-compose -f docker-compose.yml --env-file .env.production down || true
docker-compose -f docker-compose.yml --env-file .env.production build --no-cache
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Wait for services to start
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Run database migrations
echo ""
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.yml --env-file .env.production exec -T web flask db upgrade || echo "Migration failed - may already be up to date"

# Show status
echo ""
echo "📊 Deployment status:"
docker-compose -f docker-compose.yml --env-file .env.production ps

# Show logs from last few lines
echo ""
echo "📋 Recent logs:"
docker-compose -f docker-compose.yml --env-file .env.production logs --tail=20

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔍 Next steps:"
echo "1. Edit /opt/cyberhunter-portal/.env.production with your actual values"
echo "2. Set up SSL certificates for your domain"
echo "3. Configure your domain DNS to point to $SERVER_IP"
echo "4. Create admin user: docker-compose exec web flask create-admin"
ENDSSH

echo ""
echo "🎉 Deployment script completed!"
echo ""
echo "📌 Quick commands:"
echo "  View logs:    ssh -i /Users/cdodunski/.ssh/claude_code_key $SERVER_USER@$SERVER_IP 'cd $APP_DIR && docker-compose logs -f'"
echo "  Restart:      ssh -i /Users/cdodunski/.ssh/claude_code_key $SERVER_USER@$SERVER_IP 'cd $APP_DIR && docker-compose restart'"
echo "  Status:       ssh -i /Users/cdodunski/.ssh/claude_code_key $SERVER_USER@$SERVER_IP 'cd $APP_DIR && docker-compose ps'"