from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import db
from models.user import User
from models.task import Task, TaskStatus
from models.notification import Notification
from routes.auth import role_required

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@role_required(['student'])
def dashboard():
    student_id = session.get('user_id')

    # Query all task statuses assigned to this student along with Task and Professor details
    assigned_records = db.session.query(TaskStatus, Task, User)\
        .join(Task, TaskStatus.task_id == Task.id)\
        .join(User, Task.professor_id == User.id)\
        .filter(TaskStatus.student_id == student_id)\
        .order_by(Task.deadline.asc()).all()

    pending_tasks = [rec for rec in assigned_records if rec[0].status == 'Pending']
    completed_tasks = [rec for rec in assigned_records if rec[0].status == 'Completed']

    total_count = len(assigned_records)
    pending_count = len(pending_tasks)
    completed_count = len(completed_tasks)

    # Fetch recent unread notifications for student widget
    notifications = Notification.query.filter_by(student_id=student_id).order_by(Notification.created_at.desc()).limit(10).all()

    return render_template(
        'student/dashboard.html',
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        total_count=total_count,
        pending_count=pending_count,
        completed_count=completed_count,
        notifications=notifications
    )

@student_bp.route('/tasks/<int:status_id>/complete', methods=['POST'])
@role_required(['student'])
def complete_task(status_id):
    student_id = session.get('user_id')
    status_record = TaskStatus.query.filter_by(id=status_id, student_id=student_id).first_or_404()
    task = Task.query.get(status_record.task_id)

    if status_record.status == 'Pending':
        status_record.status = 'Completed'
        status_record.completed_at = datetime.utcnow()

        # Add confirmation notification
        completion_notif = Notification(
            student_id=student_id,
            task_id=task.id,
            message=f'🟢 Task Completed: "{task.title}". Reminders stopped.',
            is_read=True
        )
        db.session.add(completion_notif)

        db.session.commit()
        flash(f'Great job! Task "{task.title}" has been marked as Completed. Automated reminders stopped for this task.', 'success')
    else:
        flash(f'Task "{task.title}" is already marked as Completed.', 'info')

    return redirect(url_for('student.dashboard'))

@student_bp.route('/notifications')
@role_required(['student'])
def notifications():
    student_id = session.get('user_id')
    notification_list = Notification.query.filter_by(student_id=student_id).order_by(Notification.created_at.desc()).all()

    return render_template('student/notifications.html', notifications=notification_list)

@student_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@role_required(['student'])
def mark_read(notification_id):
    student_id = session.get('user_id')
    notif = Notification.query.filter_by(id=notification_id, student_id=student_id).first_or_404()

    notif.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for('student.notifications'))

@student_bp.route('/notifications/read-all', methods=['POST'])
@role_required(['student'])
def mark_all_read():
    student_id = session.get('user_id')
    Notification.query.filter_by(student_id=student_id, is_read=False).update({Notification.is_read: True})
    db.session.commit()

    flash('All notifications marked as read.', 'success')
    return redirect(request.referrer or url_for('student.notifications'))
