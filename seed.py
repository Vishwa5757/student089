from datetime import datetime, timedelta
from app import create_app
from database.db_config import db
from models import User, Department, Class, Faculty, Student, Task, TaskStatus, Notification

app = create_app()

def seed_database():
    with app.app_context():
        print("Resetting database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding initial data...")

        # 1. Create Admin
        admin_user = User(
            email='admin@system.com',
            full_name='System Administrator',
            role='admin',
            phone='+1-555-0100'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)

        # 2. Create Departments
        dept_cs = Department(dept_code='CS', dept_name='Computer Science & Engineering')
        dept_ee = Department(dept_code='EE', dept_name='Electrical Engineering')
        db.session.add_all([dept_cs, dept_ee])
        db.session.flush()

        # 3. Create Classes
        class_cs101 = Class(class_code='CS-101', class_name='Data Structures & Algorithms', department_id=dept_cs.id)
        class_ee201 = Class(class_code='EE-201', class_name='Digital Electronics & Circuits', department_id=dept_ee.id)
        db.session.add_all([class_cs101, class_ee201])
        db.session.flush()

        # 4. Create Faculty Users & Profiles
        faculty1_user = User(email='prof.smith@univ.edu', full_name='Dr. Alan Smith', role='faculty', phone='+1-555-0201')
        faculty1_user.set_password('faculty123')
        
        faculty2_user = User(email='prof.davis@univ.edu', full_name='Dr. Clara Davis', role='faculty', phone='+1-555-0202')
        faculty2_user.set_password('faculty123')

        db.session.add_all([faculty1_user, faculty2_user])
        db.session.flush()

        faculty1 = Faculty(user_id=faculty1_user.id, department_id=dept_cs.id, designation='Associate Professor')
        faculty2 = Faculty(user_id=faculty2_user.id, department_id=dept_ee.id, designation='Senior Lecturer')
        db.session.add_all([faculty1, faculty2])
        db.session.flush()

        # 5. Create Student Users & Profiles
        students_data = [
            ('student.john@univ.edu', 'John Doe', 'CS2026-001', dept_cs.id, class_cs101.id),
            ('student.emma@univ.edu', 'Emma Watson', 'CS2026-002', dept_cs.id, class_cs101.id),
            ('student.alex@univ.edu', 'Alex Rivera', 'EE2026-001', dept_ee.id, class_ee201.id),
            ('student.sara@univ.edu', 'Sara Connor', 'EE2026-002', dept_ee.id, class_ee201.id),
        ]

        created_students = []
        for email, name, roll, dept_id, cls_id in students_data:
            s_user = User(email=email, full_name=name, role='student', phone='+1-555-0300')
            s_user.set_password('student123')
            db.session.add(s_user)
            db.session.flush()

            s_profile = Student(user_id=s_user.id, roll_number=roll, department_id=dept_id, class_id=cls_id)
            db.session.add(s_profile)
            created_students.append(s_profile)

        db.session.flush()

        # 6. Create Initial Sample Tasks/Reminders
        now = datetime.now()
        task1 = Task(
            title='Submit Binary Search Tree Implementation Assignment',
            description='Implement BST insertion, deletion, and in-order traversal in C++/Python. Submit source code as ZIP file.',
            faculty_id=faculty1.id,
            class_id=class_cs101.id,
            deadline=now + timedelta(days=2, hours=4),
            priority='High'
        )
        task2 = Task(
            title='Midterm Project Proposal: Smart Attendance System',
            description='Submit 2-page project proposal covering problem analysis, system design, and database schema.',
            faculty_id=faculty1.id,
            class_id=class_cs101.id,
            deadline=now + timedelta(days=5),
            priority='Urgent'
        )
        task3 = Task(
            title='Lab Assignment 3: Logic Gate Simulation',
            description='Simulate AND, OR, XOR gates using Proteus/Multisim and submit lab report PDF.',
            faculty_id=faculty2.id,
            class_id=class_ee201.id,
            deadline=now + timedelta(days=3),
            priority='Medium'
        )
        db.session.add_all([task1, task2, task3])
        db.session.flush()

        # 7. Create TaskStatus records for Students in those classes
        # CS-101 Students (John, Emma)
        cs_students = [s for s in created_students if s.class_id == class_cs101.id]
        for s in cs_students:
            db.session.add(TaskStatus(task_id=task1.id, student_id=s.id, status='Pending'))
            db.session.add(TaskStatus(task_id=task2.id, student_id=s.id, status='Pending'))
            db.session.add(Notification(user_id=s.user_id, message='New Task Assigned: Submit Binary Search Tree Implementation'))

        # EE-201 Students (Alex, Sara)
        ee_students = [s for s in created_students if s.class_id == class_ee201.id]
        for s in ee_students:
            db.session.add(TaskStatus(task_id=task3.id, student_id=s.id, status='Pending'))
            db.session.add(Notification(user_id=s.user_id, message='New Task Assigned: Lab Assignment 3 Logic Gate Simulation'))

        db.session.commit()
        print("Database seeded successfully!")
        print("\nPre-seeded Accounts:")
        print("Admin:   admin@system.com / admin123")
        print("Faculty: prof.smith@univ.edu / faculty123")
        print("Student: student.john@univ.edu / student123")

if __name__ == '__main__':
    seed_database()
