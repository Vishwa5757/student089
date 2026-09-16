from datetime import datetime, date
from app import app
from models.database import db
from models.user import User
from models.task import Task, TaskStatus
from models.notification import Notification

def seed_database():
    with app.app_context():
        print("[*] Seeding database with initial college management data...")
        
        # 1. Reset/create tables
        db.create_all()

        # 2. Add Admin user if not exists
        admin = User.query.filter_by(email='admin@college.edu').first()
        if not admin:
            admin = User(name='System Administrator', email='admin@college.edu', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("[+] Admin account created: admin@college.edu / admin123")

        # 3. Add Professors
        prof1 = User.query.filter_by(email='prof.smith@college.edu').first()
        if not prof1:
            prof1 = User(name='Dr. Robert Smith', email='prof.smith@college.edu', role='professor')
            prof1.set_password('prof123')
            db.session.add(prof1)

        prof2 = User.query.filter_by(email='prof.davis@college.edu').first()
        if not prof2:
            prof2 = User(name='Prof. Sarah Davis', email='prof.davis@college.edu', role='professor')
            prof2.set_password('prof123')
            db.session.add(prof2)

        # 4. Add Students
        students = [
            {'name': 'Student A (Arun)', 'email': 'student.john@college.edu'},
            {'name': 'Student B (Ravi)', 'email': 'student.jane@college.edu'},
            {'name': 'Student C (Kumar)', 'email': 'student.alex@college.edu'},
            {'name': 'Student D (Surya)', 'email': 'student.emily@college.edu'},
        ]
        
        student_objs = []
        for s in students:
            st = User.query.filter_by(email=s['email']).first()
            if not st:
                st = User(name=s['name'], email=s['email'], role='student')
                st.set_password('student123')
                db.session.add(st)
            student_objs.append(st)

        db.session.commit()

        # Re-fetch prof1 and student objects with primary keys
        prof1 = User.query.filter_by(email='prof.smith@college.edu').first()
        st_a = User.query.filter_by(email='student.john@college.edu').first()
        st_b = User.query.filter_by(email='student.jane@college.edu').first()
        st_c = User.query.filter_by(email='student.alex@college.edu').first()

        # 5. Add Sample Task if not exists
        sample_task = Task.query.filter_by(title='Submit Internship Form').first()
        if not sample_task and prof1:
            sample_task = Task(
                title='Submit Internship Form',
                description='Complete and submit the internship form before the deadline.',
                deadline=date(2026, 10, 9),
                professor_id=prof1.id
            )
            db.session.add(sample_task)
            db.session.flush()

            # Create Pending task status records & initial notifications for Student A, Student B, Student C
            for st in [st_a, st_b, st_c]:
                if st:
                    status = TaskStatus(task_id=sample_task.id, student_id=st.id, status='Pending')
                    db.session.add(status)

                    notif = Notification(
                        student_id=st.id,
                        task_id=sample_task.id,
                        message=f'🔔 New Task Assigned: "{sample_task.title}". Deadline: 2026-10-09.',
                        is_read=False
                    )
                    db.session.add(notif)

            db.session.commit()
            print("[+] Created sample task: 'Submit Internship Form' assigned to Student A, B, and C with initial notifications.")

        print("\n==========================================")
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("==========================================")
        print("Sample Accounts:")
        print("  * Admin:     admin@college.edu      / admin123")
        print("  * Professor: prof.smith@college.edu / prof123")
        print("  * Student A: student.john@college.edu / student123")
        print("  * Student B: student.jane@college.edu / student123")
        print("==========================================\n")

if __name__ == '__main__':
    seed_database()
