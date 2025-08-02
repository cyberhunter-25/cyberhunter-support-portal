#!/bin/bash
# Commands to run on the server after SSH

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

echo "📋 Checking logs:"
docker-compose --env-file .env.production logs --tail=50