@echo off
echo ============================================================
echo 🚀 Expense Tracker - Offline Mode (Windows)
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Run setup if needed
if not exist "db.sqlite3" (
    echo 🗄️  Setting up database...
    python setup_offline.py
)

REM Start the server
echo 🚀 Starting Expense Tracker...
echo.
echo 📱 Access the application at: http://127.0.0.1:8000
echo 🔧 Admin panel at: http://127.0.0.1:8000/admin
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python run_offline.py

pause 