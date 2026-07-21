from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db_config import db
from models import Student, TaskStatus, Task, Notification
from utils.decorators import role_required

student_bp = Blueprint('student', __name__, url_prefix='/student')

def get_current_student():
    return Student.query.filter_by(user_id=session['user_id']).first()

@student_bp.route('/dashboard')
@role_required('student')
def dashboard():
    student = get_current_student()
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    # Fetch all tasks assigned to student
    student_statuses = TaskStatus.query.filter_by(student_id=student.id).all()
    
    # Filter pending vs completed
    pending_tasks = [s for s in student_statuses if s.status == 'Pending']
    completed_tasks = [s for s in student_statuses if s.status == 'Completed']

    total_assigned = len(student_statuses)
    total_completed = len(completed_tasks)
    total_pending = len(pending_tasks)

    # Sort pending by deadline ascending
    pending_tasks.sort(key=lambda s: s.task.deadline)

    # Fetch unread notifications
    notifications = Notification.query.filter_by(user_id=session['user_id'], is_read=False).all()

    now = datetime.now()

    return render_template('student/dashboard.html',
                           student=student,
                           pending_tasks=pending_tasks,
                           completed_tasks=completed_tasks,
                           total_assigned=total_assigned,
                           total_completed=total_completed,
                           total_pending=total_pending,
                           notifications=notifications,
                           now=now)


@student_bp.route('/tasks/<int:status_id>/toggle', methods=['POST'])
@role_required('student')
def toggle_task_status(status_id):
    student = get_current_student()
    task_status = TaskStatus.query.filter_by(id=status_id, student_id=student.id).first_or_404()

    remarks = request.form.get('remarks', '').strip()

    if task_status.status == 'Pending':
        task_status.status = 'Completed'
        task_status.completed_at = datetime.now(timezone.utc)
        task_status.student_remarks = remarks if remarks else 'Completed on time.'
        flash(f'Task "{task_status.task.title}" marked as Completed!', 'success')
    else:
        task_status.status = 'Pending'
        task_status.completed_at = None
        flash(f'Task "{task_status.task.title}" marked as Pending.', 'info')

    db.session.commit()
    return redirect(url_for('student.dashboard'))


@student_bp.route('/history')
@role_required('student')
def history():
    student = get_current_student()
    if not student:
        return redirect(url_for('auth.login'))

    all_statuses = TaskStatus.query.filter_by(student_id=student.id).order_by(TaskStatus.id.desc()).all()
    now = datetime.now()

    return render_template('student/task_history.html', student=student, all_statuses=all_statuses, now=now)


@student_bp.route('/notifications/clear', methods=['POST'])
@role_required('student')
def clear_notifications():
    notifications = Notification.query.filter_by(user_id=session['user_id']).all()
    for n in notifications:
        n.is_read = True
    db.session.commit()
    flash('Notifications marked as read.', 'info')
    return redirect(url_for('student.dashboard'))
