#!/bin/bash

# Agentic Honeypot Deployment Script

echo "🍯 Agentic Honeypot Deployment Script"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Set environment variables (optional)
export FLASK_ENV=production
export FLASK_DEBUG=false

# Start the application
echo "🚀 Starting Agentic Honeypot..."
echo "Server will be available at: http://localhost:8080"
echo "Health check: http://localhost:8080/health"
echo "API endpoint: http://localhost:8080/api/message"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with gunicorn for production or flask for development
if command -v gunicorn &> /dev/null; then
    echo "🔧 Running with Gunicorn (Production Mode)"
    gunicorn -w 4 -b 0.0.0.0:8080 app:app
else
    echo "🔧 Running with Flask Development Server"
    python3 app.py
fi