#!/bin/bash

# Quick fix for GitHub authentication on server

SERVER_IP="5.161.176.85"
SERVER_USER="root"

echo "🔧 Setting up GitHub access on server..."
echo ""
echo "This script will help configure GitHub access. You have two options:"
echo "1. Make repository public (easiest)"
echo "2. Set up GitHub SSH key on server"
echo ""

read -p "Choose option (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "To make your repository public:"
    echo "1. Go to: https://github.com/cyberhunter-25/cyberhunter-support-portal/settings"
    echo "2. Scroll to 'Danger Zone'"
    echo "3. Click 'Change visibility' and select 'Public'"
    echo ""
    read -p "Press Enter when done..."
    
elif [ "$choice" = "2" ]; then
    echo ""
    echo "Setting up GitHub SSH key on server..."
    
    ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
# Generate SSH key if it doesn't exist
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -C "server@cyberhunter" -f ~/.ssh/id_ed25519 -N ""
fi

echo ""
echo "========================================="
echo "Add this SSH key to your GitHub account:"
echo "========================================="
cat ~/.ssh/id_ed25519.pub
echo "========================================="
echo ""
echo "Steps:"
echo "1. Copy the key above"
echo "2. Go to: https://github.com/settings/keys"
echo "3. Click 'New SSH key'"
echo "4. Title: 'CyberHunter Production Server'"
echo "5. Paste the key and save"
ENDSSH
    
    echo ""
    read -p "Press Enter when you've added the key to GitHub..."
fi

# Now retry deployment
echo ""
echo "🚀 Retrying deployment..."
./deploy-to-server.sh