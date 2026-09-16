import atexit
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from models.database import db
from models.task import Task, TaskStatus
from models.user import User
from models.notification import Notification

scheduler = BackgroundScheduler(daemon=True)

def check_and_send_reminders(app):
    """
    Background job that runs periodically to check student task completion statuses.
    Sends automated reminders ONLY for tasks that remain in 'Pending' status.
    Stops reminders completely when status is 'Completed'.
    """
    with app.app_context():
        try:
            # Query all task assignments that are currently Pending
            pending_records = db.session.query(TaskStatus, Task, User)\
                .join(Task, TaskStatus.task_id == Task.id)\
                .join(User, TaskStatus.student_id == User.id)\
                .filter(TaskStatus.status == 'Pending').all()

            count_sent = 0

            for status_rec, task, student in pending_records:
                # Double-check task status guard
                if status_rec.status == 'Completed':
                    continue  # Stop reminder immediately if completed

                # Prevent duplicate spam within the last 55 seconds
                recent_cutoff = datetime.utcnow() - timedelta(seconds=55)
                recent_reminder = Notification.query.filter(
                    Notification.student_id == student.id,
                    Notification.task_id == task.id,
                    Notification.message.like('%Reminder%'),
                    Notification.created_at >= recent_cutoff
                ).first()

                if recent_reminder:
                    continue  # Skip duplicate execution within current minute interval

                # Generate Automated Reminder Notification
                reminder_msg = f"⏰ Reminder: Task '{task.title}' is still Pending! Deadline: {task.deadline.strftime('%Y-%m-%d')}."
                
                new_notification = Notification(
                    student_id=student.id,
                    task_id=task.id,
                    message=reminder_msg,
                    is_read=False
                )
                db.session.add(new_notification)
                count_sent += 1

                print(f"[REMINDER SCHEDULER] Sent reminder to {student.name} ({student.email}) for Task: '{task.title}'")

            if count_sent > 0:
                db.session.commit()
                print(f"[REMINDER SCHEDULER] Successfully processed and stored {count_sent} automated reminder(s).")
            else:
                print("[REMINDER SCHEDULER] No pending task reminders required at this time.")

        except Exception as e:
            db.session.rollback()
            print(f"[REMINDER SCHEDULER ERROR] Failed to run reminder job: {e}")


def init_scheduler(app):
    """Initialize and start the background scheduler."""
    if not app.config.get('REMINDER_ENABLED', True):
        print("[REMINDER SCHEDULER] Reminder scheduler is disabled in configuration.")
        return

    interval_minutes = app.config.get('REMINDER_INTERVAL_MINUTES', 1)

    # Avoid duplicate scheduler startup in Flask debug reloader
    if not scheduler.running:
        scheduler.add_job(
            func=check_and_send_reminders,
            args=[app],
            trigger="interval",
            minutes=interval_minutes,
            id="pending_task_reminder_job",
            replace_existing=True
        )
        scheduler.start()
        print(f"[REMINDER SCHEDULER] Background scheduler started! Interval: {interval_minutes} minute(s).")

        # Shut down scheduler when app exits
        atexit.register(lambda: scheduler.shutdown(wait=False))
