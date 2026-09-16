"""
Smart Student Reminder System - Automated Comprehensive System Test Suite (Phase 10)
Tests all 17 system requirements using Flask test client & ORM assertions.
"""

import sys
import unittest
from datetime import date, datetime

sys.path.insert(0, r'D:\Smart student Remainders System')
sys.path.insert(0, r'D:\Lib\site-packages')

from app import app
from models.database import db
from models.user import User
from models.task import Task, TaskStatus
from models.notification import Notification
from remind_scheduler import check_and_send_reminders

class TestSmartStudentReminderSystem(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Seed base test users
            admin = User(name='System Administrator', email='admin@college.edu', role='admin')
            admin.set_password('admin123')

            prof = User(name='Dr. Robert Smith', email='prof.smith@college.edu', role='professor')
            prof.set_password('prof123')

            st1 = User(name='Student A (John Doe)', email='student.john@college.edu', role='student')
            st1.set_password('student123')

            st2 = User(name='Student B (Jane Miller)', email='student.jane@college.edu', role='student')
            st2.set_password('student123')

            db.session.add_all([admin, prof, st1, st2])
            db.session.commit()

    def test_01_admin_login(self):
        """Test 1: Admin Login"""
        response = self.client.post('/login', data={'email': 'admin@college.edu', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

    def test_02_professor_login(self):
        """Test 2: Professor Login"""
        response = self.client.post('/login', data={'email': 'prof.smith@college.edu', 'password': 'prof123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Professor Dashboard', response.data)

    def test_03_student_login(self):
        """Test 3: Student Login"""
        response = self.client.post('/login', data={'email': 'student.john@college.edu', 'password': 'student123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Dashboard', response.data)

    def test_04_invalid_login(self):
        """Test 4: Invalid Login handling"""
        response = self.client.post('/login', data={'email': 'invalid@college.edu', 'password': 'wrongpassword'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

    def test_05_admin_user_creation(self):
        """Test 5: Admin user creation"""
        with self.client as c:
            c.post('/login', data={'email': 'admin@college.edu', 'password': 'admin123'})
            response = c.post('/admin/users/add', data={
                'name': 'New Student Account',
                'email': 'new.student@college.edu',
                'password': 'password123',
                'role': 'student'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with self.app.app_context():
                user = User.query.filter_by(email='new.student@college.edu').first()
                self.assertIsNotNone(user)
                self.assertEqual(user.name, 'New Student Account')

    def test_06_admin_user_deletion(self):
        """Test 6: Admin user deletion"""
        with self.client as c:
            c.post('/login', data={'email': 'admin@college.edu', 'password': 'admin123'})
            with self.app.app_context():
                st2 = User.query.filter_by(email='student.jane@college.edu').first()
                st2_id = st2.id

            response = c.post(f'/admin/users/{st2_id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with self.app.app_context():
                deleted_user = db.session.get(User, st2_id)
                self.assertIsNone(deleted_user)

    def test_07_to_17_full_workflow_end_to_end(self):
        """
        Tests 7 through 17:
        7. Professor task creation
        8. Student task assignment
        9. Student notification generation
        10. Student task viewing
        11. Student task completion
        12. Status update & completed_at timestamp
        13. Automatic reminder execution
        14. Reminder stopping after completion
        15. Professor status tracking & reports
        16. Logout handling
        17. Unauthorized route access prevention
        """
        # Step 7 & 8: Professor creates task & assigns Student A (John) and Student B (Jane)
        with self.client as c:
            c.post('/login', data={'email': 'prof.smith@college.edu', 'password': 'prof123'})
            with self.app.app_context():
                st_a = User.query.filter_by(email='student.john@college.edu').first()
                st_b = User.query.filter_by(email='student.jane@college.edu').first()
                st_a_id, st_b_id = st_a.id, st_b.id

            res_create = c.post('/professor/tasks/create', data={
                'title': 'Submit Internship Form',
                'description': 'Complete and submit internship form before deadline.',
                'deadline': '2026-10-09',
                'student_ids': [str(st_a_id), str(st_b_id)]
            }, follow_redirects=True)
            self.assertEqual(res_create.status_code, 200)

        # Step 9: Verify Notifications created for Student A and B
        with self.app.app_context():
            task = Task.query.filter_by(title='Submit Internship Form').first()
            self.assertIsNotNone(task)
            task_id = task.id

            notif_a = Notification.query.filter_by(student_id=st_a_id, task_id=task_id).first()
            self.assertIsNotNone(notif_a)
            self.assertIn('New Task Assigned', notif_a.message)

        # Step 10: Logout professor and login as Student A
        with self.client as c:
            c.get('/logout')
            c.post('/login', data={'email': 'student.john@college.edu', 'password': 'student123'})
            res_dash = c.get('/student/dashboard')
            self.assertEqual(res_dash.status_code, 200)
            self.assertIn(b'Submit Internship Form', res_dash.data)


        # Step 13: Background scheduler sends automated reminder to both pending students
        with self.app.app_context():
            check_and_send_reminders(self.app)
            reminders_before_a = Notification.query.filter(
                Notification.student_id == st_a_id,
                Notification.task_id == task_id,
                Notification.message.like('%Reminder%')
            ).all()
            self.assertGreaterEqual(len(reminders_before_a), 1)

        # Step 11 & 12: Student A completes task
        with self.client as c:
            c.post('/login', data={'email': 'student.john@college.edu', 'password': 'student123'})
            with self.app.app_context():
                status_a = TaskStatus.query.filter_by(student_id=st_a_id, task_id=task_id).first()
                status_a_id = status_a.id

            res_comp = c.post(f'/student/tasks/{status_a_id}/complete', follow_redirects=True)
            self.assertEqual(res_comp.status_code, 200)

            with self.app.app_context():
                updated_status_a = db.session.get(TaskStatus, status_a_id)
                self.assertEqual(updated_status_a.status, 'Completed')
                self.assertIsNotNone(updated_status_a.completed_at)
                comp_time = updated_status_a.completed_at

        # Step 14: Re-run background reminder scheduler -> Student A gets NO new reminders
        with self.app.app_context():
            count_reminders_a_before = Notification.query.filter_by(student_id=st_a_id, task_id=task_id).count()

            # Execute background reminder job again
            check_and_send_reminders(self.app)

            count_reminders_a_after = Notification.query.filter_by(student_id=st_a_id, task_id=task_id).count()

            # Verify 0 new notifications were created for Student A after task completion
            self.assertEqual(count_reminders_a_after, count_reminders_a_before)


        # Step 15: Logout student and login as Professor to view status tracking & completion report
        with self.client as c:
            c.get('/logout')
            c.post('/login', data={'email': 'prof.smith@college.edu', 'password': 'prof123'})
            res_prof_view = c.get(f'/professor/tasks/{task_id}')
            self.assertEqual(res_prof_view.status_code, 200)
            self.assertIn(b'50% Completed', res_prof_view.data)

        # Step 16: Logout
        with self.client as c:
            res_logout = c.get('/logout', follow_redirects=True)
            self.assertEqual(res_logout.status_code, 200)
            self.assertIn(b'logged out successfully', res_logout.data)

        # Step 17: Unauthorized access prevention
        with self.client as c:
            c.post('/login', data={'email': 'student.john@college.edu', 'password': 'student123'})
            res_unauth = c.get('/admin/dashboard', follow_redirects=True)
            self.assertEqual(res_unauth.status_code, 200)
            self.assertIn(b'Access denied', res_unauth.data)


if __name__ == '__main__':
    print("======================================================================")
    print("RUNNING SMART STUDENT REMINDER SYSTEM COMPREHENSIVE TEST SUITE")
    print("======================================================================")
    unittest.main(verbosity=2)
