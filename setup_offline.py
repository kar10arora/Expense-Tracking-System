#!/usr/bin/env python
"""
Offline Expense Tracker Setup
This script sets up the database and creates a default admin user for offline use.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from Tracker.models import Profile

def setup_database():
    """Set up the database with migrations."""
    print("🗄️  Setting up database...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database setup completed!")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_default_admin():
    """Create a default admin user if it doesn't exist."""
    print("👤 Creating default admin user...")
    try:
        # Check if admin user already exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@expensetracker.local',
                password='admin123'
            )
            
            # Create profile for admin user
            Profile.objects.get_or_create(
                user=admin_user,
                defaults={'role': 'admin'}
            )
            
            print("✅ Default admin user created!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  Please change the password after first login!")
        else:
            print("ℹ️  Admin user already exists")
        return True
    except Exception as e:
        print(f"❌ Admin user creation failed: {e}")
        return False

def create_sample_data():
    """Create sample data for demonstration."""
    print("📊 Creating sample data...")
    try:
        # Create a sample user if it doesn't exist
        if not User.objects.filter(username='demo').exists():
            demo_user = User.objects.create_user(
                username='demo',
                email='demo@expensetracker.local',
                password='demo123'
            )
            
            Profile.objects.get_or_create(
                user=demo_user,
                defaults={'role': 'team_member'}
            )
            
            print("✅ Sample user created!")
            print("   Username: demo")
            print("   Password: demo123")
        else:
            print("ℹ️  Sample user already exists")
        return True
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def main():
    """Main setup function."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExpenseTracker.settings')
    
    try:
        django.setup()
        print("=" * 60)
        print("🔧 Expense Tracker - Offline Setup")
        print("=" * 60)
        
        # Run setup steps
        if setup_database():
            create_default_admin()
            create_sample_data()
            
            print("=" * 60)
            print("🎉 Setup completed successfully!")
            print("=" * 60)
            print("To start the application, run:")
            print("   python run_offline.py")
            print("   or")
            print("   python manage.py runserver")
            print("=" * 60)
        else:
            print("❌ Setup failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 