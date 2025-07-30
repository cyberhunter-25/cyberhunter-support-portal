#!/bin/bash
# Development setup script for CyberHunter Security Portal

echo "🚀 Setting up CyberHunter Security Portal Development Environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)"; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements/dev.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p app/static/uploads

# Initialize database
echo "🗄️  Initializing database..."
export FLASK_APP=run.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create initial admin user
echo "👤 Creating admin user..."
flask create-admin

# Create test company
echo "🏢 Creating test company..."
flask create-test-company

echo "✅ Development setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  flask run --debug"
echo ""
echo "Or use: make dev"