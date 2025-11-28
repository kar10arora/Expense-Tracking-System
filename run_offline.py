#!/usr/bin/env python
"""
Offline Expense Tracker Runner
This script runs the Django development server optimized for offline use.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Run the Django server for offline use."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExpenseTracker.settings')
    
    try:
        django.setup()
        print("=" * 60)
        print("🚀 Expense Tracker - Offline Mode")
        print("=" * 60)
        print("📱 Access the application at: http://127.0.0.1:8000")
        print("🔧 Admin panel at: http://127.0.0.1:8000/admin")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the development server
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 