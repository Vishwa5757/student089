from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db_config import db
from models import Faculty, Task, TaskStatus, Class, Student, Notification
from utils.decorators import role_required

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

def get_current_faculty():
    return Faculty.query.filter_by(user_id=session['user_id']).first()

@faculty_bp.route('/dashboard')
@role_required('faculty')
def dashboard():
    faculty = get_current_faculty()
    if not faculty:
        flash('Faculty profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    tasks = Task.query.filter_by(faculty_id=faculty.id).order_by(Task.deadline.asc()).all()
    classes = Class.query.filter_by(department_id=faculty.department_id).all()

    # Calculate statistics
    total_tasks = len(tasks)
    active_tasks = sum(1 for t in tasks if t.deadline >= datetime.now())
    expired_tasks = total_tasks - active_tasks

    # Calculate overall student completion rate for faculty tasks
    total_assignments = 0
    completed_assignments = 0
    for task in tasks:
        statuses = TaskStatus.query.filter_by(task_id=task.id).all()
        total_assignments += len(statuses)
        completed_assignments += sum(1 for s in statuses if s.status == 'Completed')

    completion_rate = round((completed_assignments / total_assignments * 100), 1) if total_assignments > 0 else 0

    return render_template('faculty/dashboard.html',
                           faculty=faculty,
                           tasks=tasks,
                           classes=classes,
                           total_tasks=total_tasks,
                           active_tasks=active_tasks,
                           expired_tasks=expired_tasks,
                           completion_rate=completion_rate)


@faculty_bp.route('/tasks/create', methods=['POST'])
@role_required('faculty')
def create_task():
    faculty = get_current_faculty()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    class_id = request.form.get('class_id')
    deadline_str = request.form.get('deadline')
    priority = request.form.get('priority', 'Medium')

    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    except (ValueError, TypeError):
        flash('Invalid deadline format.', 'danger')
        return redirect(url_for('faculty.dashboard'))

    task = Task(title=title, description=description, faculty_id=faculty.id,
                class_id=class_id, deadline=deadline, priority=priority)
    db.session.add(task)
    db.session.flush()

    # Automatically generate TaskStatus records & Notifications for all students in assigned class
    students = Student.query.filter_by(class_id=class_id).all()
    for student in students:
        status_record = TaskStatus(task_id=task.id, student_id=student.id, status='Pending')
        db.session.add(status_record)

        # Notify student
        notif = Notification(user_id=student.user_id, message=f'New Task Assigned: "{title}" due on {deadline.strftime("%b %d, %Y %I:%M %p")}')
        db.session.add(notif)

    db.session.commit()
    flash(f'Task "{title}" created and assigned to {len(students)} student(s)!', 'success')
    return redirect(url_for('faculty.dashboard'))


@faculty_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@role_required('faculty')
def delete_task(task_id):
    faculty = get_current_faculty()
    task = Task.query.filter_by(id=task_id, faculty_id=faculty.id).first_or_404()

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.', 'info')
    return redirect(url_for('faculty.dashboard'))


@faculty_bp.route('/tasks/<int:task_id>/status')
@role_required('faculty')
def task_status(task_id):
    faculty = get_current_faculty()
    task = Task.query.filter_by(id=task_id, faculty_id=faculty.id).first_or_404()

    student_statuses = TaskStatus.query.filter_by(task_id=task.id).all()
    total_students = len(student_statuses)
    completed_count = sum(1 for s in student_statuses if s.status == 'Completed')
    pending_count = total_students - completed_count

    return render_template('faculty/task_status.html',
                           task=task,
                           student_statuses=student_statuses,
                           total_students=total_students,
                           completed_count=completed_count,
                           pending_count=pending_count)
