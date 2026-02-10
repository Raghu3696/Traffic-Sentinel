#!/bin/bash

# Intelligent Rate Limiter - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Intelligent Rate Limiter - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Redis
echo ""
echo "📋 Checking Redis..."
if command -v redis-cli &> /dev/null; then
    echo "   ✅ Redis CLI found"
    if redis-cli ping &> /dev/null; then
        echo "   ✅ Redis is running"
    else
        echo "   ⚠️  Redis is installed but not running"
        echo "      Start Redis with: redis-server"
    fi
else
    echo "   ⚠️  Redis not found. You can:"
    echo "      1. Install Redis locally, or"
    echo "      2. Use Docker Compose (recommended)"
fi

# Create virtual environment
echo ""
echo "🔨 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✅ Dependencies installed"

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✅ Created .env file from .env.example"
    echo "   ℹ️  You can customize settings in .env"
else
    echo "   ℹ️  .env file already exists"
fi

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo ""
echo "📚 Quick Start:"
echo ""
echo "1. Start Redis (if not using Docker):"
echo "   redis-server"
echo ""
echo "2. Or use Docker Compose:"
echo "   docker-compose up -d"
echo ""
echo "3. Run the application:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "4. In another terminal, run the demo:"
echo "   source venv/bin/activate"
echo "   python test_traffic.py"
echo ""
echo "5. Monitor in real-time:"
echo "   source venv/bin/activate"
echo "   python monitor.py"
echo ""
echo "📖 Documentation: README.md"
echo "🌐 API Docs: http://localhost:8000/docs (when running)"
echo ""
echo "Happy coding! 🎉"
