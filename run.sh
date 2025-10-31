#!/bin/bash
# Quick start script for Training Data Bot Web App

echo "🚀 Starting Training Data Bot..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create directories
mkdir -p uploads outputs

# Run the app
echo "✅ Starting web server..."
echo "🌐 Open http://localhost:8000 in your browser"
echo ""
python app.py

