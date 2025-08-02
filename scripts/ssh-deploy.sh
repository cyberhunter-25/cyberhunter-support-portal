#!/bin/bash

# SSH Deployment Helper for CyberHunter Support Portal
# This script helps manage SSH connections and deployments

# Configuration
SERVER_USER="root"  # Change this to your server username
SERVER_IP=""        # Set your server IP here
SERVER_NAME="cyberhunter-prod"  # Friendly name for SSH config

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

case "$1" in
    "setup")
        echo -e "${BLUE}Setting up SSH configuration...${NC}"
        
        # Get server IP if not set
        if [ -z "$SERVER_IP" ]; then
            read -p "Enter your server IP address: " SERVER_IP
        fi
        
        # Add to SSH config
        echo -e "\nHost $SERVER_NAME
    HostName $SERVER_IP
    User $SERVER_USER
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3" >> ~/.ssh/config
        
        echo -e "${GREEN}✅ SSH config added! You can now use: ssh $SERVER_NAME${NC}"
        
        # Copy SSH key
        echo -e "\n${BLUE}Copying SSH key to server...${NC}"
        ssh-copy-id -i ~/.ssh/id_ed25519.pub $SERVER_USER@$SERVER_IP
        ;;
        
    "connect")
        echo -e "${BLUE}Connecting to server...${NC}"
        ssh $SERVER_NAME
        ;;
        
    "deploy")
        echo -e "${BLUE}Deploying to production server...${NC}"
        
        # Create deployment script
        cat << 'EOF' > /tmp/remote-deploy.sh
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Navigate to app directory
cd /opt/cyberhunter-portal || { 
    echo "Creating application directory..."
    mkdir -p /opt/cyberhunter-portal
    cd /opt/cyberhunter-portal
}

# Clone or pull latest code
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes..."
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/cyberhunter-25/cyberhunter-support-portal.git .
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
fi

# Build and deploy
echo "🔨 Building application..."
docker-compose down || true
docker-compose build --no-cache
docker-compose up -d

echo "✅ Deployment complete!"
echo "🔍 Checking service status..."
docker-compose ps
EOF
        
        # Execute on remote server
        ssh $SERVER_NAME 'bash -s' < /tmp/remote-deploy.sh
        rm /tmp/remote-deploy.sh
        ;;
        
    "logs")
        echo -e "${BLUE}Fetching logs from server...${NC}"
        ssh $SERVER_NAME "cd /opt/cyberhunter-portal && docker-compose logs --tail=100 -f"
        ;;
        
    "status")
        echo -e "${BLUE}Checking server status...${NC}"
        ssh $SERVER_NAME "cd /opt/cyberhunter-portal && docker-compose ps"
        ;;
        
    "exec")
        # Execute arbitrary command on server
        shift
        ssh $SERVER_NAME "$@"
        ;;
        
    *)
        echo -e "${GREEN}CyberHunter SSH Deployment Helper${NC}"
        echo ""
        echo "Usage: $0 {setup|connect|deploy|logs|status|exec}"
        echo ""
        echo "  setup    - Configure SSH access to your server"
        echo "  connect  - SSH into the server"
        echo "  deploy   - Deploy latest code to production"
        echo "  logs     - View application logs"
        echo "  status   - Check service status"
        echo "  exec     - Execute command on server"
        echo ""
        echo "Examples:"
        echo "  $0 setup                    # Initial setup"
        echo "  $0 deploy                   # Deploy to production"
        echo "  $0 exec 'df -h'            # Check disk space"
        echo "  $0 exec 'docker ps'        # List containers"
        ;;
esac