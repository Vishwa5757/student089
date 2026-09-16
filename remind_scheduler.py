import os
import sys
from datetime import datetime
from app import create_app
from database.db_config import db
from models import Task, TaskStatus, Notification
from utils.email_service import send_task_reminder_email

app = create_app()

def scan_and_remind(app_instance=None):
    """
    Scans for pending tasks on their final submission day (deadline date)
    and dispatches 10-minute interval email reminders and in-app notifications.
    """
    target_app = app_instance or app
    with target_app.app_context():
        now = datetime.now()
        reminders_sent = 0
        
        # Interval in minutes (default 10, configurable via env for demo/testing)
        interval_minutes = int(os.environ.get('REMINDER_INTERVAL_MINUTES', 10))
        interval_seconds = interval_minutes * 60

        # 1. Fetch all tasks where deadline date is today
        tasks = Task.query.all()
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Scanning {len(tasks)} task(s) for final submission day reminders (interval={interval_minutes}m)...")

        for task in tasks:
            # 2. Check whether today is the deadline date
            if task.deadline.date() != now.date():
                continue

            # 3. Check if deadline has already passed
            if now >= task.deadline:
                # Deadline reached or passed - stop reminders
                # Optionally transition pending task statuses to 'Overdue'
                overdue_statuses = TaskStatus.query.filter_by(task_id=task.id, status='Pending').all()
                for ost in overdue_statuses:
                    ost.status = 'Overdue'
                db.session.commit()
                continue

            # 4. Fetch PENDING student task statuses only (STOP WHEN STUDENT COMPLETES)
            pending_statuses = TaskStatus.query.filter_by(task_id=task.id, status='Pending').all()

            for status in pending_statuses:
                student = status.student
                if not student or not student.user:
                    continue
                user = student.user

                # 5. DUPLICATE PREVENTION: Check if interval has elapsed since last reminder
                last_sent = status.last_reminder_sent_at
                
                # Fallback check against Notification table if last_reminder_sent_at is None
                if not last_sent:
                    last_notif = Notification.query.filter_by(
                        user_id=user.id,
                        task_id=task.id,
                        notification_type='REMINDER_10MIN'
                    ).order_by(Notification.created_at.desc()).first()
                    if last_notif:
                        last_sent = last_notif.created_at

                if last_sent:
                    elapsed_seconds = (now - last_sent).total_seconds()
                    # Allow 10-second margin for 1-minute scheduler execution jitter
                    if elapsed_seconds < (interval_seconds - 10):
                        # 10-minute interval has not yet elapsed - skip duplicate email
                        continue

                deadline_str = task.deadline.strftime("%d %B %Y, %I:%M %p")

                # 6. Dispatch Email Reminder
                try:
                    email_success = send_task_reminder_email(
                        to_email=user.email,
                        student_name=user.full_name,
                        task_title=task.title,
                        deadline_str=deadline_str
                    )
                    if not email_success:
                        print(f"[SCHEDULER] Email sending returned false for task {task.id} / student {user.email}", file=sys.stderr)
                except Exception as e:
                    print(f"[SCHEDULER ERROR] Email reminder failed for task {task.id}: {str(e)}", file=sys.stderr)
                    # Do not mark as sent so scheduler can retry on next interval safely
                    continue

                # 7. Create In-App Notification & Save Last Reminder Timestamp
                notif_msg = f"🔔 Task Reminder: {task.title} is still pending. Last date: {deadline_str}."
                new_notif = Notification(
                    user_id=user.id,
                    task_id=task.id,
                    notification_type='REMINDER_10MIN',
                    message=notif_msg
                )
                db.session.add(new_notif)

                # Save reminder timestamp to prevent duplicates
                status.last_reminder_sent_at = now
                db.session.commit()
                reminders_sent += 1

        print(f"Scan complete. Reminders created/sent: {reminders_sent}")
        return reminders_sent

if __name__ == '__main__':
    scan_and_remind()

