import pytest
from datetime import datetime, timedelta
from app import create_app
from database.db_config import db
from models import User, Department, Class, Faculty, Student, Task, TaskStatus, Notification
from remind_scheduler import scan_and_remind
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        dept = Department(dept_code="CS", dept_name="Computer Science")
        db.session.add(dept)
        db.session.flush()

        cls = Class(class_code="CS101", class_name="Data Structures", department_id=dept.id)
        db.session.add(cls)
        db.session.flush()

        fac_user = User(email="faculty@test.com", full_name="Prof. Test", role="faculty")
        fac_user.set_password("fac123")
        db.session.add(fac_user)
        db.session.flush()

        fac = Faculty(user_id=fac_user.id, department_id=dept.id, designation="Professor")
        db.session.add(fac)
        db.session.flush()

        stu_user = User(email="student@test.com", full_name="Student Test", role="student")
        stu_user.set_password("stu123")
        db.session.add(stu_user)
        db.session.flush()

        stu = Student(user_id=stu_user.id, roll_number="CS-001", department_id=dept.id, class_id=cls.id)
        db.session.add(stu)
        db.session.flush()

        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_stage_1_initial_task_notification(app, client):
    """TEST 1: Normal task assignment creates ONE initial notification."""
    client.post('/auth/login', data={'email': 'faculty@test.com', 'password': 'fac123'})
    
    now = datetime.now()
    deadline = (now + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M')
    
    with app.app_context():
        cls = Class.query.first()
        res = client.post('/faculty/tasks/create', data={
            'title': 'Test Assignment 1',
            'description': 'Details',
            'class_id': cls.id,
            'student_id': 'all',
            'priority': 'Medium',
            'deadline': deadline
        }, follow_redirects=True)
        assert res.status_code == 200

        stu_user = User.query.filter_by(email="student@test.com").first()
        notifs = Notification.query.filter_by(user_id=stu_user.id, notification_type='TASK_ASSIGNED').all()
        assert len(notifs) == 1
        assert "New task assigned: Test Assignment 1" in notifs[0].message

def test_before_final_day_no_reminders(app):
    """TEST 2: Task deadline several days away should NOT receive final-hour reminders."""
    with app.app_context():
        fac = Faculty.query.first()
        cls = Class.query.first()
        stu = Student.query.first()

        now = datetime.now()
        task = Task(
            title="Future Task",
            faculty_id=fac.id,
            class_id=cls.id,
            deadline=now + timedelta(days=3),
            priority="Low"
        )
        db.session.add(task)
        db.session.flush()

        status = TaskStatus(task_id=task.id, student_id=stu.id, status="Pending")
        db.session.add(status)
        db.session.commit()

    reminders_sent = scan_and_remind(app_instance=app)
    assert reminders_sent == 0

def test_final_day_6_stage_reminders_and_duplicate_prevention(app):
    """TEST 4 & TEST 5: Final-day 1-hour reminders and duplicate prevention."""
    with app.app_context():
        fac = Faculty.query.first()
        cls = Class.query.first()
        stu = Student.query.first()

        now = datetime.now()
        # Set deadline to 25 minutes from now (Today, final hour -> REMINDER_30 stage)
        task = Task(
            title="Urgent Assignment",
            faculty_id=fac.id,
            class_id=cls.id,
            deadline=now + timedelta(minutes=25),
            priority="Urgent"
        )
        db.session.add(task)
        db.session.flush()

        status = TaskStatus(task_id=task.id, student_id=stu.id, status="Pending")
        db.session.add(status)
        db.session.commit()

        # Run 1: Should send 1 reminder (REMINDER_30)
        r1 = scan_and_remind(app_instance=app)
        assert r1 == 1

        # Run 2 immediately: DUPLICATE PREVENTION -> 0 sent!
        r2 = scan_and_remind(app_instance=app)
        assert r2 == 0

        # Verify notification type in DB
        notif = Notification.query.filter_by(user_id=stu.user_id, task_id=task.id, notification_type='REMINDER_30').first()
        assert notif is not None
        assert "30 minutes remain" in notif.message

def test_task_completion_stops_reminders(app, client):
    """TEST 6: Marking task completed immediately stops future reminders."""
    with app.app_context():
        fac = Faculty.query.first()
        cls = Class.query.first()
        stu = Student.query.first()

        now = datetime.now()
        task = Task(
            title="Lab Project",
            faculty_id=fac.id,
            class_id=cls.id,
            deadline=now + timedelta(minutes=15),
            priority="High"
        )
        db.session.add(task)
        db.session.flush()

        status = TaskStatus(task_id=task.id, student_id=stu.id, status="Pending")
        db.session.add(status)
        db.session.commit()
        status_id = status.id

    # 1. Run scheduler while Pending -> REMINDER_20 sent
    r1 = scan_and_remind(app_instance=app)
    assert r1 == 1

    # 2. Student completes task
    client.post('/auth/login', data={'email': 'student@test.com', 'password': 'stu123'})
    client.post(f'/student/tasks/{status_id}/toggle', data={'remarks': 'Finished early'}, follow_redirects=True)

    # 3. Verify status is Completed
    with app.app_context():
        updated_status = db.session.get(TaskStatus, status_id)
        assert updated_status.status == "Completed"

    # 4. Re-run scheduler -> 0 sent!
    r2 = scan_and_remind(app_instance=app)
    assert r2 == 0

def test_deadline_passed_no_reminders(app):
    """TEST 7: Expired tasks after deadline generate no reminders."""
    with app.app_context():
        fac = Faculty.query.first()
        cls = Class.query.first()
        stu = Student.query.first()

        now = datetime.now()
        task = Task(
            title="Past Due Task",
            faculty_id=fac.id,
            class_id=cls.id,
            deadline=now - timedelta(minutes=10),
            priority="High"
        )
        db.session.add(task)
        db.session.flush()

        status = TaskStatus(task_id=task.id, student_id=stu.id, status="Pending")
        db.session.add(status)
        db.session.commit()

    reminders_sent = scan_and_remind(app_instance=app)
    assert reminders_sent == 0
