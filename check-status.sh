#!/bin/bash

SERVER_IP="5.161.176.85"

echo "🔍 Checking CyberHunter Portal Status"
echo "====================================="

ssh root@$SERVER_IP << 'ENDSSH'
cd /opt/cyberhunter-portal

echo ""
echo "📊 Docker Services Status:"
docker-compose --env-file .env.production ps

echo ""
echo "🔍 Checking Port 5000:"
netstat -tlpn | grep :5000 || echo "Port 5000 not listening"

echo ""
echo "📋 Recent Logs:"
docker-compose --env-file .env.production logs --tail=20 web

echo ""
echo "🔧 Restarting services..."
docker-compose --env-file .env.production restart

sleep 5

echo ""
echo "📊 New Status:"
docker-compose --env-file .env.production ps
ENDSSH