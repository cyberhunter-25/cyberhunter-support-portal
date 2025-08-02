#!/bin/bash

# Fix deployment after requirements update

SERVER_IP="5.161.176.85"
SERVER_USER="root"

echo "🔧 Fixing deployment..."

ssh -t $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /opt/cyberhunter-portal

echo "📥 Pulling latest changes with requirements files..."
git pull origin main

echo "🔨 Rebuilding containers..."
docker-compose --env-file .env.production build --no-cache

echo "🚀 Starting services..."
docker-compose --env-file .env.production up -d

echo "⏳ Waiting for services..."
sleep 10

echo "📊 Current status:"
docker-compose --env-file .env.production ps

echo "✅ Fix complete!"
ENDSSH