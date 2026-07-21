from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_config import db
from models import User, Department, Class, Faculty, Student, Task
from utils.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    total_students = Student.query.count()
    total_faculty = Faculty.query.count()
    total_departments = Department.query.count()
    total_classes = Class.query.count()
    total_tasks = Task.query.count()

    recent_students = Student.query.order_by(Student.id.desc()).limit(5).all()
    recent_faculty = Faculty.query.order_by(Faculty.id.desc()).limit(5).all()
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_faculty=total_faculty,
                           total_departments=total_departments,
                           total_classes=total_classes,
                           total_tasks=total_tasks,
                           recent_students=recent_students,
                           recent_faculty=recent_faculty,
                           recent_tasks=recent_tasks)


@admin_bp.route('/students', methods=['GET', 'POST'])
@role_required('admin')
def manage_students():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            roll_number = request.form.get('roll_number', '').strip()
            department_id = request.form.get('department_id')
            class_id = request.form.get('class_id')
            phone = request.form.get('phone', '').strip()

            if User.query.filter_by(email=email).first():
                flash('Email already registered!', 'danger')
            elif Student.query.filter_by(roll_number=roll_number).first():
                flash('Roll number already exists!', 'danger')
            else:
                user = User(email=email, full_name=full_name, role='student', phone=phone)
                user.set_password(password if password else 'student123')
                db.session.add(user)
                db.session.flush()

                student = Student(user_id=user.id, roll_number=roll_number,
                                  department_id=department_id, class_id=class_id)
                db.session.add(student)
                db.session.commit()
                flash('Student added successfully!', 'success')

        elif action == 'delete':
            student_id = request.form.get('student_id')
            student = Student.query.get(student_id)
            if student:
                user = student.user
                db.session.delete(student)
                if user:
                    db.session.delete(user)
                db.session.commit()
                flash('Student deleted successfully.', 'success')

        return redirect(url_for('admin.manage_students'))

    students = Student.query.all()
    departments = Department.query.all()
    classes = Class.query.all()
    return render_template('admin/manage_students.html', students=students, departments=departments, classes=classes)


@admin_bp.route('/faculty', methods=['GET', 'POST'])
@role_required('admin')
def manage_faculty():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            department_id = request.form.get('department_id')
            designation = request.form.get('designation', 'Professor').strip()
            phone = request.form.get('phone', '').strip()

            if User.query.filter_by(email=email).first():
                flash('Email already registered!', 'danger')
            else:
                user = User(email=email, full_name=full_name, role='faculty', phone=phone)
                user.set_password(password if password else 'faculty123')
                db.session.add(user)
                db.session.flush()

                faculty = Faculty(user_id=user.id, department_id=department_id, designation=designation)
                db.session.add(faculty)
                db.session.commit()
                flash('Faculty member added successfully!', 'success')

        elif action == 'delete':
            faculty_id = request.form.get('faculty_id')
            faculty = Faculty.query.get(faculty_id)
            if faculty:
                user = faculty.user
                db.session.delete(faculty)
                if user:
                    db.session.delete(user)
                db.session.commit()
                flash('Faculty member deleted successfully.', 'success')

        return redirect(url_for('admin.manage_faculty'))

    faculty_list = Faculty.query.all()
    departments = Department.query.all()
    return render_template('admin/manage_faculty.html', faculty_list=faculty_list, departments=departments)


@admin_bp.route('/departments', methods=['GET', 'POST'])
@role_required('admin')
def manage_departments():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_dept':
            dept_code = request.form.get('dept_code', '').strip().upper()
            dept_name = request.form.get('dept_name', '').strip()
            if Department.query.filter_by(dept_code=dept_code).first():
                flash('Department code already exists!', 'danger')
            else:
                dept = Department(dept_code=dept_code, dept_name=dept_name)
                db.session.add(dept)
                db.session.commit()
                flash('Department created successfully!', 'success')

        elif action == 'add_class':
            class_code = request.form.get('class_code', '').strip().upper()
            class_name = request.form.get('class_name', '').strip()
            department_id = request.form.get('department_id')
            if Class.query.filter_by(class_code=class_code).first():
                flash('Class code already exists!', 'danger')
            else:
                cls = Class(class_code=class_code, class_name=class_name, department_id=department_id)
                db.session.add(cls)
                db.session.commit()
                flash('Class created successfully!', 'success')

        elif action == 'delete_dept':
            dept_id = request.form.get('dept_id')
            dept = Department.query.get(dept_id)
            if dept:
                db.session.delete(dept)
                db.session.commit()
                flash('Department deleted successfully.', 'success')

        elif action == 'delete_class':
            class_id = request.form.get('class_id')
            cls = Class.query.get(class_id)
            if cls:
                db.session.delete(cls)
                db.session.commit()
                flash('Class deleted successfully.', 'success')

        return redirect(url_for('admin.manage_departments'))

    departments = Department.query.all()
    classes = Class.query.all()
    return render_template('admin/manage_departments.html', departments=departments, classes=classes)
