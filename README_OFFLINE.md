# Expense Tracker - Offline Version

A complete offline-capable expense tracking application built with Django.

## 🚀 Quick Start (Offline Mode)

### Prerequisites
- Python 3.8 or higher
- No internet connection required after initial setup

### Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Setup Script**
   ```bash
   python setup_offline.py
   ```
   This will:
   - Set up the database
   - Create default admin user
   - Create sample demo user

3. **Start the Application**
   ```bash
   python run_offline.py
   ```
   Or use the traditional method:
   ```bash
   python manage.py runserver
   ```

4. **Access the Application**
   - Main application: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin

## 👤 Default Users

### Admin User
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** Admin (full access)

### Demo User
- **Username:** `demo`
- **Password:** `demo123`
- **Role:** Team Member

⚠️ **Security Note:** Change default passwords after first login!

## 🔧 Offline Features

### ✅ What Works Offline
- Complete expense tracking functionality
- User authentication and authorization
- Dashboard with charts and analytics
- Expense submission and management
- Report generation (PDF/Excel)
- File upload for invoices
- All CRUD operations

### 📊 Features
- **Dashboard:** Visual charts and expense overview
- **Add Expenses:** Submit new expense entries
- **My Submissions:** View and manage your expenses
- **Reports:** Generate detailed expense reports
- **Admin Panel:** Full administrative control
- **Role-based Access:** Different permissions for different user types

### 🗄️ Database
- Uses SQLite database (`db.sqlite3`)
- No external database connection required
- All data stored locally

### 📁 File Storage
- Invoice uploads stored in `media/invoices/`
- Static files served locally
- No external CDN dependencies

## 🛠️ Offline Optimizations

### Settings Changes
- `ALLOWED_HOSTS = ['*']` - Accepts connections from any host
- `TIME_ZONE = 'UTC'` - Universal timezone for consistency
- `SESSION_COOKIE_AGE = 86400` - 24-hour sessions for convenience
- `SESSION_EXPIRE_AT_BROWSER_CLOSE = False` - Sessions persist across browser restarts

### Security Considerations
- HTTPS disabled for local development
- CSRF protection still active
- Session security maintained
- File upload validation active

## 📋 Available Commands

### Setup Commands
```bash
# Initial setup
python setup_offline.py

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Commands
```bash
# Start server
python run_offline.py
python manage.py runserver

# Collect static files
python manage.py collectstatic

# Shell access
python manage.py shell
```

### Database Commands
```bash
# Reset database
rm db.sqlite3
python setup_offline.py

# Backup database
cp db.sqlite3 backup_$(date +%Y%m%d_%H%M%S).sqlite3
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port 8000
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Database Locked**
   ```bash
   # Restart the application
   # If persistent, delete db.sqlite3 and run setup again
   ```

3. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic
   ```

4. **Permission Errors**
   ```bash
   # Ensure write permissions on media/ directory
   chmod 755 media/
   ```

### Logs
- Check console output for error messages
- Django debug mode is enabled for detailed error information

## 📱 Usage Guide

### For Regular Users
1. Login with your credentials
2. Navigate to "Add Expense" to submit new expenses
3. View "My Submissions" to manage your expenses
4. Use "Dashboard" to see expense analytics
5. Generate "Reports" for detailed expense summaries

### For Administrators
1. Login with admin credentials
2. Access admin panel at `/admin`
3. Manage users, expenses, and system settings
4. Approve expenses (if role-based approval is enabled)
5. Generate system-wide reports

## 🔒 Security Best Practices

### For Production Use
1. Change default passwords immediately
2. Enable HTTPS in settings
3. Set `DEBUG = False`
4. Configure proper `ALLOWED_HOSTS`
5. Use strong secret keys
6. Regular database backups

### Data Protection
- All data stored locally in SQLite
- No external data transmission
- File uploads validated and sanitized
- Session data encrypted

## 📞 Support

This is a self-contained offline application. All functionality is available without internet connectivity after initial setup.

For issues:
1. Check the troubleshooting section
2. Review console error messages
3. Verify file permissions
4. Ensure Python dependencies are installed

---

**Note:** This application is designed for offline use. All features work without internet connectivity once the initial setup is complete. 