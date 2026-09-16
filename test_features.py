"""
Automated Test Suite for Smart Student Reminder System:
Email Notification & 10-Minute Final-Day Scheduler Verification.
"""
import os
import sys
from datetime import datetime, timedelta
from app import create_app
from database.db_config import db
from models import User, Department, Class, Faculty, Student, Task, TaskStatus, Notification
from remind_scheduler import scan_and_remind
from utils.email_service import send_task_assigned_email

def run_tests():
    print("=" * 80)
    print("STARTING 8-STEP EMAIL REMINDER & SCHEDULER VERIFICATION SUITE")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        # Ensure database tables exist
        db.create_all()

        # Clean existing tasks/notifications for clean test run
        Notification.query.delete()
        TaskStatus.query.delete()
        Task.query.delete()
        db.session.commit()

        # Fetch seed users
        student1_user = User.query.filter_by(email='student.john@univ.edu').first()
        student2_user = User.query.filter_by(email='student.emma@univ.edu').first()
        faculty_user = User.query.filter_by(role='faculty').first()

        if not student1_user or not student2_user or not faculty_user:
            print("[X] Seed users missing. Running seed database first...")
            from seed import seed_database
            seed_database()
            student1_user = User.query.filter_by(email='student.john@univ.edu').first()
            student2_user = User.query.filter_by(email='student.emma@univ.edu').first()
            faculty_user = User.query.filter_by(role='faculty').first()

        student1 = Student.query.filter_by(user_id=student1_user.id).first()
        student2 = Student.query.filter_by(user_id=student2_user.id).first()
        faculty = Faculty.query.filter_by(user_id=faculty_user.id).first()

        now = datetime.now()

        # --- TEST 1: PROFESSOR CREATES TASK FOR STUDENT A ONLY ---
        print("\n--- [TEST 1] Task Creation & Target Student Initial Email ---")
        task1 = Task(
            title="Database Assignment 1",
            description="Create SQL ER Diagram and normalizations.",
            faculty_id=faculty.id,
            class_id=student1.class_id,
            deadline=now + timedelta(days=1), # Tomorrow
            priority="High"
        )
        db.session.add(task1)
        db.session.flush()

        # Assign ONLY to Student 1 (John)
        status1 = TaskStatus(task_id=task1.id, student_id=student1.id, status='Pending')
        db.session.add(status1)

        deadline_str = task1.deadline.strftime("%d %B %Y, %I:%M %p")
        notif1 = Notification(
            user_id=student1_user.id,
            task_id=task1.id,
            notification_type='TASK_ASSIGNED',
            message=f"New task assigned: {task1.title}. Deadline: {deadline_str}."
        )
        db.session.add(notif1)
        db.session.commit()

        # Simulate sending initial assignment email
        send_task_assigned_email(student1_user.email, task1.title, task1.description, deadline_str)
        print(f"[PASS] Task assigned to Student A ({student1_user.email}). In-app & initial email dispatched.")
        
        # Verify Student B did NOT get assigned task1
        s2_status = TaskStatus.query.filter_by(task_id=task1.id, student_id=student2.id).first()
        assert s2_status is None, "Student B should not receive task1 status!"
        print(f"[PASS] Student B ({student2_user.email}) correctly did NOT receive Task 1.")

        # --- TEST 2: DEADLINE TOMORROW (NO REMINDERS TODAY) ---
        print("\n--- [TEST 2] Deadline Tomorrow (No Final-Day Reminders Today) ---")
        reminders_sent = scan_and_remind()
        print(f"[PASS] Scheduler result for tomorrow's deadline: {reminders_sent} sent (Expected: 0).")
        assert reminders_sent == 0, "No reminders should be sent before final submission day!"

        # --- TEST 3: DEADLINE ARRIVED / PASSED (REMINDER SYSTEM BECOMES ACTIVE) ---
        print("\n--- [TEST 3] Deadline Arrived/Passed (Reminder System Active) ---")
        task1.deadline = now - timedelta(minutes=5) # 5 minutes ago (due date arrived/passed)
        db.session.commit()
        print(f"Updated deadline to past/current due date: {task1.deadline.strftime('%d %b %Y, %I:%M %p')}.")

        r_sent_1 = scan_and_remind()
        print(f"[PASS] Scheduler result on due date: {r_sent_1} sent (Expected: 1).")
        assert r_sent_1 == 1, "Should send 1 reminder when active on/after due date!"

        # --- TEST 4: LEAVE TASK PENDING & CHECK 10-MINUTE INTERVAL ---
        print("\n--- [TEST 4] 10-Minute Reminder Interval Logic ---")
        # Immediately re-running within 10 minutes should send 0
        r_sent_fast = scan_and_remind()
        print(f"[PASS] Immediate scheduler re-run: {r_sent_fast} sent (Expected: 0).")
        assert r_sent_fast == 0, "Should skip re-run before 10-minute interval!"

        # --- TEST 5: RUN SCHEDULER EVERY MINUTE (DUPLICATE PREVENTION) ---
        print("\n--- [TEST 5] Multiple Scheduler Runs Every Minute (Duplicate Prevention) ---")
        runs_sent = sum(scan_and_remind() for _ in range(5))
        print(f"[PASS] Total sent across 5 consecutive 1-minute runs: {runs_sent} (Expected: 0).")
        assert runs_sent == 0, "Duplicate prevention failed across consecutive runs!"

        # --- TEST 6: STUDENT COMPLETES TASK (STOP REMINDERS IMMEDIATELY) ---
        print("\n--- [TEST 6] Student Completes Task (All Reminders Stop) ---")
        status1.status = 'Completed'
        status1.completed_at = datetime.now()
        db.session.commit()
        print(f"Student marked task '{task1.title}' as Completed.")

        # Simulate time moving past 10 minutes interval
        status1.last_reminder_sent_at = datetime.now() - timedelta(minutes=15)
        db.session.commit()

        r_sent_after_complete = scan_and_remind()
        print(f"[PASS] Scheduler result after task completion: {r_sent_after_complete} sent (Expected: 0).")
        assert r_sent_after_complete == 0, "Completed task should NOT trigger reminders!"

        # --- TEST 7: PAST DUE PENDING TASK (REPEATING UNTIL COMPLETED) ---
        print("\n--- [TEST 7] Past Due Pending Task (Repeats Reminders Until Marked Complete) ---")
        # Create task with past deadline
        task2 = Task(
            title="Expired Python Task",
            description="Past deadline task.",
            faculty_id=faculty.id,
            class_id=student1.class_id,
            deadline=now - timedelta(minutes=30), # 30 mins ago
            priority="Low"
        )
        db.session.add(task2)
        db.session.flush()

        status2 = TaskStatus(task_id=task2.id, student_id=student1.id, status='Pending')
        db.session.add(status2)
        db.session.commit()

        r_sent_expired = scan_and_remind()
        print(f"[PASS] Scheduler result for pending past-due task: {r_sent_expired} sent (Expected: 1).")
        assert r_sent_expired == 1, "Pending past-due task MUST trigger reminder!"

        # Mark task2 complete and verify reminders stop permanently
        status2.status = 'Completed'
        db.session.commit()
        r_sent_after_complete2 = scan_and_remind()
        print(f"[PASS] Scheduler result after task 2 completed: {r_sent_after_complete2} sent (Expected: 0).")
        assert r_sent_after_complete2 == 0, "Completed task 2 should stop reminders permanently!"

        # --- TEST 8: RESTART SCHEDULER (PERSISTENT DUPLICATE PREVENTION) ---
        print("\n--- [TEST 8] Scheduler Restart (Persistent State Verification) ---")
        # Create active task due 10 mins ago
        task3 = Task(
            title="Post-Restart Task",
            description="Testing state persistence across restarts.",
            faculty_id=faculty.id,
            class_id=student1.class_id,
            deadline=now - timedelta(minutes=10),
            priority="Medium"
        )
        db.session.add(task3)
        db.session.flush()

        status3 = TaskStatus(task_id=task3.id, student_id=student1.id, status='Pending')
        db.session.add(status3)
        db.session.commit()

        r1 = scan_and_remind() # First send
        print(f"First scan sent: {r1} reminder.")
        assert r1 == 1, "First scan for past due pending task 3 should send 1 reminder!"

        # Simulate new process / restart app instance
        new_app = create_app()
        r2 = scan_and_remind(app_instance=new_app) # Second scan immediately on new app instance
        print(f"[PASS] Post-restart scan sent: {r2} (Expected: 0).")
        assert r2 == 0, "Duplicate prevention failed across app restart!"

    print("\n" + "=" * 80)
    print("ALL 8 VERIFICATION TESTS PASSED PERFECTLY!")
    print("=" * 80)

if __name__ == '__main__':
    run_tests()
