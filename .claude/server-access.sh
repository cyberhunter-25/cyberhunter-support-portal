#!/bin/bash

# Server Access Helper for Claude Code
# This allows Claude to execute commands on your server

SERVER_NAME="cyberhunter-prod"  # Update this if you use a different SSH config name

# Function to execute commands on server
remote_exec() {
    ssh $SERVER_NAME "$@"
}

# Function to deploy to server
remote_deploy() {
    echo "🚀 Deploying to production..."
    
    # Push local changes first
    echo "📤 Pushing local changes to GitHub..."
    git push
    
    # Deploy on server
    ssh $SERVER_NAME << 'ENDSSH'
cd /opt/cyberhunter-portal || mkdir -p /opt/cyberhunter-portal && cd /opt/cyberhunter-portal

# Pull latest changes
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/cyberhunter-25/cyberhunter-support-portal.git .
fi

# Deploy with Docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Show status
docker-compose ps
ENDSSH
}

# Main logic
case "$1" in
    "exec")
        shift
        remote_exec "$@"
        ;;
    "deploy")
        remote_deploy
        ;;
    "test")
        echo "Testing connection to $SERVER_NAME..."
        remote_exec "echo '✅ Connection successful!'; uname -a"
        ;;
    *)
        echo "Usage: $0 {exec|deploy|test}"
        echo "  exec <command>  - Execute command on server"
        echo "  deploy         - Deploy latest code"
        echo "  test           - Test SSH connection"
        ;;
esac