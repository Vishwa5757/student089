from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.faculty import faculty_bp
from routes.student import student_bp

__all__ = ['auth_bp', 'admin_bp', 'faculty_bp', 'student_bp']
