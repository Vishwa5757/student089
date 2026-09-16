from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import db
from models.user import User
from models.task import Task
from routes.auth import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required(['admin'])
def dashboard():
    total_professors = User.query.filter_by(role='professor').count()
    total_students = User.query.filter_by(role='student').count()
    total_admins = User.query.filter_by(role='admin').count()
    total_tasks = Task.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_professors=total_professors,
        total_students=total_students,
        total_admins=total_admins,
        total_tasks=total_tasks,
        recent_users=recent_users
    )

@admin_bp.route('/users')
@role_required(['admin'])
def users():
    role_filter = request.args.get('role', '').strip()
    search_query = request.args.get('q', '').strip()

    query = User.query

    if role_filter in ['admin', 'professor', 'student']:
        query = query.filter_by(role=role_filter)

    if search_query:
        query = query.filter(
            (User.name.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%'))
        )

    user_list = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=user_list, role_filter=role_filter, search_query=search_query)

@admin_bp.route('/users/add', methods=['POST'])
@role_required(['admin'])
def add_user():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', '').strip()

    if not name or not email or not password or role not in ['admin', 'professor', 'student']:
        flash('All fields are required and role must be valid.', 'danger')
        return redirect(url_for('admin.users'))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('A user with this email address already exists.', 'danger')
        return redirect(url_for('admin.users'))

    new_user = User(name=name, email=email, role=role)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    flash(f'{role.capitalize()} "{name}" added successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@role_required(['admin'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', '').strip()
    new_password = request.form.get('password', '').strip()

    if not name or not email or role not in ['admin', 'professor', 'student']:
        flash('Name, email, and valid role are required.', 'danger')
        return redirect(url_for('admin.users'))

    # Check if email changed and is taken
    if email != user.email:
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('That email address is already in use by another account.', 'danger')
            return redirect(url_for('admin.users'))

    user.name = name
    user.email = email
    user.role = role

    if new_password:
        user.set_password(new_password)

    db.session.commit()
    flash(f'User "{user.name}" updated successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@role_required(['admin'])
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot delete your own logged-in admin account.', 'warning')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    user_name = user.name
    db.session.delete(user)
    db.session.commit()

    flash(f'User "{user_name}" has been deleted.', 'success')
    return redirect(url_for('admin.users'))
