import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-student-reminder-key-2026'
    
    # MySQL details
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'student_reminder_db')
    
    if os.environ.get('TESTING', 'false').lower() in ['true', '1']:
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    elif os.environ.get('USE_MYSQL', 'false').lower() in ['true', '1']:
        # Ensure target MySQL database schema exists before SQLAlchemy initializes
        try:
            import pymysql
            _conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                port=int(MYSQL_PORT)
            )
            with _conn.cursor() as _cursor:
                _cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4;")
            _conn.close()
        except Exception:
            pass

        from urllib.parse import quote_plus
        encoded_password = quote_plus(MYSQL_PASSWORD)
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        # Production connection pooling parameters
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 10,
            'pool_recycle': 3600,
            'pool_pre_ping': True
        }
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'student_reminder.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail / SMTP settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
