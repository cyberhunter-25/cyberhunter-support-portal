#!/bin/bash

# Install GitHub CLI on macOS

echo "Installing GitHub CLI..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install GitHub CLI
brew install gh

# Check installation
if command -v gh &> /dev/null; then
    echo "GitHub CLI installed successfully!"
    echo "Now run: gh auth login"
else
    echo "Installation failed. Please install manually."
fi