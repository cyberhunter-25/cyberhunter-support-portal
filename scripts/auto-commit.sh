#!/bin/bash

# Auto-commit and push script for CyberHunter Support Portal
# Usage: ./scripts/auto-commit.sh "commit message"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if commit message is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide a commit message${NC}"
    echo "Usage: $0 \"your commit message\""
    exit 1
fi

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}Error: Not in a git repository${NC}"
        exit 1
    fi
}

# Function to commit and push
auto_commit_push() {
    echo -e "${GREEN}Starting auto-commit process...${NC}"
    
    # Check git status
    echo "Checking git status..."
    git status --short
    
    # Add all changes
    echo -e "\n${GREEN}Adding all changes...${NC}"
    git add .
    
    # Commit with provided message
    echo -e "\n${GREEN}Committing changes...${NC}"
    git commit -m "$1" -m "🤖 Auto-committed by Claude Code" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}Pushing to remote...${NC}"
        git push
        
        if [ $? -eq 0 ]; then
            echo -e "\n${GREEN}✅ Successfully pushed to GitHub!${NC}"
        else
            echo -e "\n${RED}❌ Push failed. You may need to pull first or resolve conflicts.${NC}"
            echo "Try: git pull --rebase origin main"
        fi
    else
        echo -e "\n${RED}❌ Commit failed. There may be no changes to commit.${NC}"
    fi
}

# Main execution
check_git_repo
auto_commit_push "$1"