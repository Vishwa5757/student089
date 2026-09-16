from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import db
from models.user import User
from models.task import Task, TaskStatus
from routes.auth import role_required

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

@professor_bp.route('/dashboard')
@role_required(['professor'])
def dashboard():
    prof_id = session.get('user_id')
    tasks = Task.query.filter_by(professor_id=prof_id).order_by(Task.created_at.desc()).all()

    total_tasks = len(tasks)
    total_assigned_records = sum(t.total_assigned for t in tasks)
    total_completed_records = sum(t.completed_count for t in tasks)
    total_pending_records = sum(t.pending_count for t in tasks)

    overall_completion_rate = round((total_completed_records / total_assigned_records * 100)) if total_assigned_records > 0 else 0

    return render_template(
        'professor/dashboard.html',
        tasks=tasks,
        total_tasks=total_tasks,
        total_assigned_records=total_assigned_records,
        total_completed_records=total_completed_records,
        total_pending_records=total_pending_records,
        overall_completion_rate=overall_completion_rate
    )

@professor_bp.route('/tasks/create', methods=['GET', 'POST'])
@role_required(['professor'])
def create_task():
    # Fetch all students available to assign tasks to
    students = User.query.filter_by(role='student').order_by(User.name.asc()).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        deadline_str = request.form.get('deadline', '').strip()
        selected_student_ids = request.form.getlist('student_ids')

        if not title or not deadline_str:
            flash('Task title and deadline date are required.', 'danger')
            return render_template('professor/create_task.html', students=students)

        if not selected_student_ids:
            flash('Please select at least one student to assign the task to.', 'danger')
            return render_template('professor/create_task.html', students=students)

        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format for deadline.', 'danger')
            return render_template('professor/create_task.html', students=students)

        prof_id = session.get('user_id')

        # 1. Create the Task
        new_task = Task(
            title=title,
            description=description,
            deadline=deadline,
            professor_id=prof_id
        )
        db.session.add(new_task)
        db.session.flush() # Flush to obtain new_task.id

        # 2. Automatically create Pending task_status & Notification for each selected student
        from models.notification import Notification
        assigned_count = 0
        for student_id in selected_student_ids:
            try:
                sid = int(student_id)
                status_record = TaskStatus(
                    task_id=new_task.id,
                    student_id=sid,
                    status='Pending'
                )
                db.session.add(status_record)

                # Generate initial task assigned notification
                notification = Notification(
                    student_id=sid,
                    task_id=new_task.id,
                    message=f'🔔 New Task Assigned: "{title}". Deadline: {deadline_str}.',
                    is_read=False
                )
                db.session.add(notification)

                assigned_count += 1
            except ValueError:
                continue

        db.session.commit()
        flash(f'Task "{title}" created successfully and assigned to {assigned_count} student(s)!', 'success')
        return redirect(url_for('professor.dashboard'))


    return render_template('professor/create_task.html', students=students)

@professor_bp.route('/tasks/<int:task_id>')
@role_required(['professor'])
def task_detail(task_id):
    prof_id = session.get('user_id')
    task = Task.query.filter_by(id=task_id, professor_id=prof_id).first_or_404()

    status_filter = request.args.get('status', 'all').strip().lower()

    # Query all student status records for this task
    base_query = db.session.query(TaskStatus, User)\
        .join(User, TaskStatus.student_id == User.id)\
        .filter(TaskStatus.task_id == task.id)

    all_records = base_query.order_by(User.name.asc()).all()

    # Calculate completion report metrics
    total_assigned = len(all_records)
    completed_count = sum(1 for status, u in all_records if status.status == 'Completed')
    pending_count = sum(1 for status, u in all_records if status.status == 'Pending')
    completion_rate = round((completed_count / total_assigned * 100)) if total_assigned > 0 else 0

    # Filter status records according to user selection
    if status_filter == 'pending':
        filtered_records = [r for r in all_records if r[0].status == 'Pending']
    elif status_filter == 'completed':
        filtered_records = [r for r in all_records if r[0].status == 'Completed']
    else:
        filtered_records = all_records

    return render_template(
        'professor/task_detail.html',
        task=task,
        status_records=filtered_records,
        status_filter=status_filter,
        total_assigned=total_assigned,
        completed_count=completed_count,
        pending_count=pending_count,
        completion_rate=completion_rate
    )

