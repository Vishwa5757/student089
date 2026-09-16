import os
from flask import Flask, session
from config import Config
from models.database import db
from models.user import User
from models.task import Task, TaskStatus
from models.notification import Notification
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.professor import professor_bp
from routes.student import student_bp
from remind_scheduler import init_scheduler

def try_setup_mysql():
    """Attempt to create the MySQL database if connection is available."""
    try:
        import pymysql
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT,
            connect_timeout=3
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        connection.close()
        print(f"[+] MySQL Database '{Config.MYSQL_DB}' ready.")
        return True
    except Exception as e:
        print(f"[!] Warning: Could not connect to MySQL server ({e}).")
        return False

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Check if MySQL server is reachable
    mysql_ok = try_setup_mysql()
    if not mysql_ok:
        print(f"[*] Falling back to SQLite database for active session: {Config.SQLITE_URI}")
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLITE_URI

    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(student_bp)

    # Context processors: Inject datetime and unread notification counter for student UI
    @app.context_processor
    def inject_global_vars():
        from datetime import datetime
        unread_count = 0
        if 'user_id' in session and session.get('user_role') == 'student':
            unread_count = Notification.query.filter_by(
                student_id=session.get('user_id'),
                is_read=False
            ).count()
        return {
            'now': datetime.utcnow(),
            'unread_notification_count': unread_count
        }

    with app.app_context():
        try:
            db.create_all()
            print("[+] Database tables initialized.")
        except Exception as e:
            print(f"[!] Error creating tables: {e}")

    # Initialize Automated Reminder Background Scheduler
    init_scheduler(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
