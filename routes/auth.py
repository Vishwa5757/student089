from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db_config import db
from models.user import User
from utils.decorators import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('user_role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'faculty':
            return redirect(url_for('faculty.dashboard'))
        elif role == 'student':
            return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.full_name
            session['user_role'] = user.role

            flash(f'Welcome back, {user.full_name}!', 'success')

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'faculty':
                return redirect(url_for('faculty.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid email address or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        new_password = request.form.get('new_password', '').strip()

        if full_name:
            user.full_name = full_name
            session['user_name'] = full_name
        user.phone = phone

        if new_password:
            user.set_password(new_password)
            flash('Password updated successfully.', 'success')

        db.session.commit()
        flash('Profile details updated.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', user=user)
