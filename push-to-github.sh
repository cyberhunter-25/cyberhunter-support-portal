#!/bin/bash
# Script to push CyberHunter Security Portal to GitHub

echo "🚀 Preparing to push to GitHub..."

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit - CyberHunter Security Support Portal

- Complete dual authentication system (OAuth + Local)
- Multi-factor authentication (MFA) support
- Docker containerization for easy deployment
- Dark cyber security theme
- Automated deployment scripts
- Production-ready configuration"

# Get GitHub details
echo ""
echo "📋 Please provide your GitHub repository details:"
read -p "GitHub username: " username
read -p "Repository name (e.g., cyberhunter-portal): " repo_name

# Add remote
echo "🔗 Adding GitHub remote..."
git remote add origin "https://github.com/${username}/${repo_name}.git"

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "✅ Done! Your code is now on GitHub at:"
echo "   https://github.com/${username}/${repo_name}"
echo ""
echo "📥 To clone on your server:"
echo "   git clone https://github.com/${username}/${repo_name}.git"