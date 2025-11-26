#!/bin/bash
# Quick Start Script for Manuel El Manual

set -e  # Exit on error

echo "================================"
echo "🚀 Manuel El Manual - Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your credentials:"
    echo "   - GCP_PROJECT_ID"
    echo "   - MANUALS_BUCKET"
    echo "   - GOOGLE_API_KEY"
    echo ""
    read -p "Press Enter after you've updated .env to continue..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# Check GCP authentication
echo ""
echo "🔐 Checking GCP authentication..."
if gcloud auth application-default print-access-token &> /dev/null; then
    echo "✅ GCP authentication OK"
else
    echo "⚠️  GCP authentication not configured"
    echo "📝 Run: gcloud auth application-default login"
    read -p "Do you want to authenticate now? (y/n): " auth_now
    if [ "$auth_now" = "y" ]; then
        gcloud auth application-default login
    fi
fi

# Display next steps
echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo "1. Make sure you've configured .env with your credentials"
echo "2. Create BigQuery tables (run: bq query < setup_bigquery.sql)"
echo "3. Create GCS bucket for manuals"
echo "4. Start the server: python main.py"
echo ""
echo "🌐 The app will be available at: http://127.0.0.1:8080"
echo ""
echo "================================"
