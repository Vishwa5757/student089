from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = session.get('user_role')
            if user_role not in roles:
                flash('Access denied. You do not have permission to view this page.', 'danger')
                # Redirect to user's home dashboard based on role
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'professor':
                    return redirect(url_for('professor.dashboard'))
                elif user_role == 'student':
                    return redirect(url_for('student.dashboard'))
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        user_role = session.get('user_role')
        if user_role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user_role == 'professor':
            return redirect(url_for('professor.dashboard'))
        elif user_role == 'student':
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.role

            flash(f'Welcome back, {user.name}!', 'success')

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'professor':
                return redirect(url_for('professor.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
