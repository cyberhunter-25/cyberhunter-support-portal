#!/bin/bash

# Git Helper for Claude Code
# This script provides git operations that Claude can use

case "$1" in
    "status")
        git status --porcelain
        ;;
    "add-all")
        git add .
        echo "Added all changes"
        ;;
    "commit")
        shift
        git commit -m "$@" -m "🤖 Generated with Claude Code" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
        ;;
    "push")
        git push
        ;;
    "pull")
        git pull
        ;;
    "diff")
        git diff --staged
        ;;
    "log")
        git log --oneline -10
        ;;
    "auto")
        # Auto commit and push with message
        shift
        if [ -z "$1" ]; then
            echo "Error: Commit message required"
            exit 1
        fi
        git add .
        git commit -m "$@" -m "🤖 Generated with Claude Code" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
        git push
        ;;
    *)
        echo "Usage: $0 {status|add-all|commit|push|pull|diff|log|auto}"
        echo "  status    - Show git status"
        echo "  add-all   - Add all changes"
        echo "  commit    - Commit with message"
        echo "  push      - Push to remote"
        echo "  pull      - Pull from remote"
        echo "  diff      - Show staged changes"
        echo "  log       - Show recent commits"
        echo "  auto      - Add, commit, and push in one command"
        exit 1
        ;;
esac