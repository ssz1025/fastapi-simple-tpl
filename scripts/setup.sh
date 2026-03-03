#!/bin/bash
# Database setup script
# Usage: ./scripts/setup.sh

set -e

echo "🔧 Setting up FastAPI project..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $python_version"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Create logs directory
mkdir -p logs

# Copy env file if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Initialize database
echo "🗄️  Initializing database..."
python scripts/init_db.py

echo "✅ Setup complete!"
echo ""
echo "Run the server:"
echo "  ./scripts/run.py"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
