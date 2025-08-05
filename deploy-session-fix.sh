#!/bin/bash

# Deploy Flask-Session Redis Fix to Production Server
# This script deploys the fixed configuration to guardian.clirsec.com

echo "=== Deploying Flask-Session Redis Fix ==="
echo "Timestamp: $(date)"
echo

# Server details
SERVER="guardian.clirsec.com"
SERVER_DIR="/opt/cyberhunter-portal"
ENV_FILE=".env.production.configured"

echo "1. Copying fixed files to server..."

# Copy the three critical files
echo "Copying app/extensions.py..."
scp app/extensions.py root@$SERVER:$SERVER_DIR/app/extensions.py

echo "Copying .env.production.configured..."
scp .env.production.configured root@$SERVER:$SERVER_DIR/.env.production.configured

echo "Copying docker-compose.yml..."
scp docker-compose.yml root@$SERVER:$SERVER_DIR/docker-compose.yml

echo
echo "2. Connecting to server to restart containers..."

ssh root@$SERVER << 'ENDSSH'
cd /opt/cyberhunter-portal

echo "Current directory: $(pwd)"
echo "Files present:"
ls -la app/extensions.py .env.production.configured docker-compose.yml

echo
echo "Stopping containers..."
docker-compose --env-file .env.production.configured down

echo
echo "Starting containers with updated configuration..."
docker-compose --env-file .env.production.configured up -d

echo
echo "Waiting for containers to start..."
sleep 15

echo
echo "Checking container status..."
docker-compose --env-file .env.production.configured ps

echo
echo "Checking web container logs for Redis connection..."
echo "Recent logs from web container:"
docker-compose --env-file .env.production.configured logs web | tail -20

echo
echo "Testing application..."
curl -f http://localhost:5000/health 2>/dev/null && echo "✓ Health check passed" || echo "✗ Health check failed"

echo
echo "Testing main page (should not get 500 error)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Main page returned 200 OK"
elif [ "$HTTP_CODE" = "500" ]; then 
    echo "✗ Main page still returning 500 error"
else
    echo "? Main page returned HTTP $HTTP_CODE"
fi

echo
echo "Final status check..."
docker-compose --env-file .env.production.configured ps
ENDSSH

echo
echo "=== Deployment Complete ==="
echo "Check the output above for any errors."
echo "If still getting 500 errors, SSH to server and check logs:"
echo "ssh root@$SERVER"
echo "cd /opt/cyberhunter-portal"
echo "docker-compose --env-file .env.production.configured logs web"