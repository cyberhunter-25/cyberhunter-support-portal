#!/bin/bash

# Fix Flask-Session Redis Connection
# This script fixes the 500 error caused by Flask-Session trying to connect to localhost instead of redis container

echo "=== CyberHunter Portal - Fix Session Redis Connection ==="
echo "Timestamp: $(date)"
echo

# Set variables
REPO_DIR="/opt/cyberhunter-portal"
ENV_FILE=".env.production.configured"

echo "1. Checking current directory structure..."
pwd
ls -la

echo
echo "2. Copying fixed files to server..."

# Copy the fixed files (this assumes the script is run from the local repo and files are copied to server)
echo "Files that need to be updated on server:"
echo "- app/extensions.py (Flask-Session Redis configuration)"
echo "- .env.production.configured (SESSION_REDIS_URL environment variable)" 
echo "- docker-compose.yml (SESSION_REDIS_URL in environment section)"

echo
echo "3. Stopping containers..."
cd $REPO_DIR
docker-compose --env-file $ENV_FILE down

echo
echo "4. Starting containers with updated configuration..."
docker-compose --env-file $ENV_FILE up -d

echo
echo "5. Checking container status..."
docker-compose --env-file $ENV_FILE ps

echo
echo "6. Checking web container logs for Redis connection..."
echo "Looking for Flask-Session Redis connection in logs..."
docker-compose --env-file $ENV_FILE logs web | grep -i redis | tail -10

echo
echo "7. Testing the application..."
echo "Waiting 10 seconds for containers to start..."
sleep 10

# Test the application
echo "Testing application health..."
curl -f http://localhost:5000/health 2>/dev/null && echo "✓ Health check passed" || echo "✗ Health check failed"

echo
echo "Testing main page..."
curl -f http://localhost:5000/ 2>/dev/null >/dev/null && echo "✓ Main page accessible" || echo "✗ Main page failed"

echo
echo "8. Final container status..."
docker-compose --env-file $ENV_FILE ps

echo
echo "=== Fix Session Redis Connection Complete ==="
echo "If you're still getting 500 errors, check the logs with:"
echo "docker-compose --env-file $ENV_FILE logs web"