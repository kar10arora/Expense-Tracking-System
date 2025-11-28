#!/bin/bash

echo "============================================================"
echo "🚀 Expense Tracker - Offline Mode (Unix/Linux)"
echo "============================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run setup if needed
if [ ! -f "db.sqlite3" ]; then
    echo "🗄️  Setting up database..."
    python setup_offline.py
fi

# Start the server
echo "🚀 Starting Expense Tracker..."
echo
echo "📱 Access the application at: http://127.0.0.1:8000"
echo "🔧 Admin panel at: http://127.0.0.1:8000/admin"
echo
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo

python run_offline.py 