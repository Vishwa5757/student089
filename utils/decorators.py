from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                flash('Access denied: You do not have permission to view this resource.', 'danger')
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'faculty':
                    return redirect(url_for('faculty.dashboard'))
                elif user_role == 'student':
                    return redirect(url_for('student.dashboard'))
                else:
                    return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
