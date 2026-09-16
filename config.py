import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-student-reminder-secret-key-2026'
    
    # MySQL Database Settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'smart_student_reminder'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)

    # Primary MySQL Connection URI
    MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    
    # Fallback SQLite URI (in case MySQL driver or daemon is unavailable during dev)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLITE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'smart_student_reminder.db')}"

    # Default to MySQL URI; app.py will select SQLITE_URI if MySQL fails to connect
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or MYSQL_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Automatic Reminder System Settings
    REMINDER_INTERVAL_MINUTES = int(os.environ.get('REMINDER_INTERVAL_MINUTES') or 1)
    REMINDER_ENABLED = os.environ.get('REMINDER_ENABLED', 'True').lower() in ('true', '1', 't')


