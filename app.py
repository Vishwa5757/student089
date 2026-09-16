import os
from flask import Flask, redirect, url_for, session
from config import Config
from database.db_config import db
from routes import auth_bp, admin_bp, faculty_bp, student_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    from utils.email_service import mail
    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(student_bp)

    # Initialize background scheduler for task reminders
    if not app.config.get('TESTING') and not os.environ.get('DISABLE_SCHEDULER'):
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            try:
                from apscheduler.schedulers.background import BackgroundScheduler
                from remind_scheduler import scan_and_remind

                interval_minutes = int(os.environ.get('REMINDER_INTERVAL_MINUTES', 10))
                scheduler = BackgroundScheduler(daemon=True)
                scheduler.add_job(
                    func=lambda: scan_and_remind(app),
                    trigger='interval',
                    minutes=interval_minutes,
                    id='task_reminder_job',
                    replace_existing=True
                )
                scheduler.start()
            except Exception as e:
                print(f"Background scheduler initialization notice: {e}")

    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('user_role')
            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'faculty':
                return redirect(url_for('faculty.dashboard'))
            elif role == 'student':
                return redirect(url_for('student.dashboard'))
        return redirect(url_for('auth.login'))

    # Custom Jinja filters
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%b %d, %Y %I:%M %p'):
        if value is None:
            return ''
        return value.strftime(format)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
