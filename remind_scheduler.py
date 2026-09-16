import os
import sys
from datetime import datetime
from database.db_config import db
from models import Task, TaskStatus, Notification
from utils.email_service import send_task_reminder_email

def scan_and_remind(app_instance=None):
    """
    Scans for pending tasks whose due date (deadline) has passed
    and dispatches 10-minute interval email reminders and in-app notifications.
    Repeats with NO upper limit until the student marks the task complete.
    """
    if app_instance:
        ctx = app_instance.app_context()
        ctx.push()
    else:
        from app import create_app
        target_app = create_app()
        ctx = target_app.app_context()
        ctx.push()

    try:
        now = datetime.now()
        reminders_sent = 0
        
        # Interval in minutes (default 10, configurable via env for demo/testing)
        interval_minutes = int(os.environ.get('REMINDER_INTERVAL_MINUTES', 10))
        interval_seconds = interval_minutes * 60

        # Fetch all PENDING student task statuses where task due date has passed
        pending_statuses = TaskStatus.query.join(Task).filter(
            TaskStatus.status == 'Pending',
            Task.deadline <= now
        ).all()

        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Scanning {len(pending_statuses)} pending task status(es) due on/before now (interval={interval_minutes}m)...")

        for status in pending_statuses:
            task = status.task
            student = status.student
            if not task or not student or not student.user:
                continue
            user = student.user

            # Check if interval has elapsed since last reminder
            last_sent = status.last_reminder_sent_at
            
            # Fallback check against Notification table if last_reminder_sent_at is None
            if not last_sent:
                last_notif = Notification.query.filter_by(
                    user_id=user.id,
                    task_id=task.id
                ).filter(
                    Notification.notification_type.in_(['reminder', 'REMINDER_10MIN'])
                ).order_by(Notification.created_at.desc()).first()
                if last_notif:
                    last_sent = last_notif.created_at

            if last_sent:
                elapsed_seconds = (now - last_sent).total_seconds()
                # Allow 10-second margin for execution jitter
                if elapsed_seconds < (interval_seconds - 10):
                    continue

            deadline_str = task.deadline.strftime("%d %B %Y, %I:%M %p")

            # Dispatch Email Reminder to assignee login email
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
                continue

            # Create In-App Notification ('reminder')
            notif_msg = f"🔔 Task Reminder: {task.title} is still pending. Last date: {deadline_str}."
            new_notif = Notification(
                user_id=user.id,
                task_id=task.id,
                notification_type='reminder',
                message=notif_msg
            )
            db.session.add(new_notif)

            # Update reminder timestamp and count
            status.last_reminder_sent_at = now
            status.reminder_count = (status.reminder_count or 0) + 1
            db.session.commit()
            reminders_sent += 1

        print(f"Scan complete. Reminders created/sent: {reminders_sent}")
        return reminders_sent
    finally:
        ctx.pop()


if __name__ == '__main__':
    scan_and_remind()
