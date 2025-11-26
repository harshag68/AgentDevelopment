#!/bin/bash
# run.sh - Simple script to run the Manuel El Manual server

echo "🚀 Starting Manuel El Manual Server..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: ./quickstart.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from template..."
    cp .env.example .env
    echo "✅ Created .env - Please edit it with your credentials"
    echo ""
fi

# Activate virtual environment and run
echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo "▶️  Starting server..."
echo ""
python main.py
