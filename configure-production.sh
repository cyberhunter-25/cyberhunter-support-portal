#!/bin/bash

# Production configuration helper
SERVER_IP="5.161.176.85"

echo "🔧 CyberHunter Portal - Production Configuration"
echo "=============================================="
echo ""

# Check current configuration
echo "📋 Let's check what needs to be configured..."
echo ""

ssh root@$SERVER_IP << 'ENDSSH'
cd /opt/cyberhunter-portal

echo "Current .env.production status:"
if [ -f .env.production ]; then
    echo "✅ File exists"
    echo ""
    echo "Current configuration (sensitive values hidden):"
    grep -E "^[A-Z_]+=" .env.production | sed 's/=.*/=***/' | head -20
else
    echo "❌ File missing - creating from template"
    cp .env.example .env.production 2>/dev/null || echo "No template found"
fi
ENDSSH

echo ""
echo "📝 You need to configure the following:"
echo ""
echo "1. DOMAIN CONFIGURATION"
echo "   - What domain/subdomain will you use?"
echo "   - Example: support.cyberhunter.com or portal.clirsec.com"
echo ""
echo "2. OAUTH PROVIDERS"
echo ""
echo "   Microsoft Azure:"
echo "   - Go to: https://portal.azure.com"
echo "   - App registrations → New registration"
echo "   - Redirect URI: https://YOUR_DOMAIN/auth/callback/microsoft"
echo "   - Get: Application (client) ID and Client Secret"
echo ""
echo "   Google Cloud:"
echo "   - Go to: https://console.cloud.google.com"
echo "   - APIs & Services → Credentials → Create Credentials → OAuth client ID"
echo "   - Redirect URI: https://YOUR_DOMAIN/auth/callback/google"
echo "   - Get: Client ID and Client Secret"
echo ""
echo "3. EMAIL CONFIGURATION (guardian@clirsec.com)"
echo "   - Enable 2FA on Gmail account"
echo "   - Generate app password at: https://myaccount.google.com/apppasswords"
echo "   - Use the app password (NOT your regular Gmail password)"
echo ""
echo "4. SECURITY KEYS"
echo "   - Generate secure random strings for:"
echo "     - FLASK_SECRET_KEY (use: openssl rand -hex 32)"
echo "     - DB_PASSWORD (use: openssl rand -hex 16)"
echo "     - REDIS_PASSWORD (use: openssl rand -hex 16)"
echo ""

# Generate example secure keys
echo "🔑 Here are some secure random values you can use:"
echo ""
echo "FLASK_SECRET_KEY=$(openssl rand -hex 32)"
echo "DB_PASSWORD=$(openssl rand -hex 16)"
echo "REDIS_PASSWORD=$(openssl rand -hex 16)"
echo ""

echo "📝 To edit the configuration on the server:"
echo "ssh root@$SERVER_IP"
echo "cd /opt/cyberhunter-portal"
echo "nano .env.production"
echo ""
echo "After editing, restart services:"
echo "docker-compose --env-file .env.production restart"