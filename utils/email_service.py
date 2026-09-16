import sys
from flask import current_app
from flask_mail import Mail, Message

mail = Mail()

def _send_email(to_email, subject, body):
    """
    Internal helper to send email via Flask-Mail if configured,
    or print to sys.stdout (console) as fallback simulation.
    """
    username = current_app.config.get('MAIL_USERNAME') or ''
    password = current_app.config.get('MAIL_PASSWORD') or ''
    is_real_smtp = username and password and 'your_gmail' not in username and 'your_app_password' not in password

    if is_real_smtp:
        try:
            msg = Message(
                subject=subject,
                recipients=[to_email],
                body=body
            )
            mail.send(msg)
            print(f"[EMAIL] Sent email to {to_email} | Subject: {subject}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email to {to_email}: {str(e)}", file=sys.stderr)
            return False
    else:
        # Development/Demo fallback to terminal logs
        print("\n" + "="*60)
        print(f"[EMAIL LOG SIMULATION] (SMTP not configured in .env)")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("="*60 + "\n")
        return True


def send_task_assigned_email(to_email, task_title, description, deadline_str):
    """
    Sends an initial email notification to the student about an assigned task.
    """
    subject = f"New Task Assigned - {task_title}"
    body = (
        f"Hello,\n\n"
        f"A new task has been assigned to you.\n\n"
        f"Task: {task_title}\n"
        f"Description: {description or 'No additional description provided.'}\n"
        f"Last Date of Submission: {deadline_str}\n\n"
        f"Please complete the task before the deadline.\n\n"
        f"Smart Student Reminder System"
    )
    return _send_email(to_email, subject, body)


def send_task_reminder_email(to_email, student_name, task_title, deadline_str):
    """
    Sends a reminder email to the student on the final submission day if task is pending.
    """
    subject = f"Reminder - {task_title} Still Pending"
    body = (
        f"Hello {student_name},\n\n"
        f"This is a reminder that your task is still pending.\n\n"
        f"Task:\n{task_title}\n\n"
        f"Last Date of Submission:\n{deadline_str}\n\n"
        f"Please complete the task before the deadline.\n\n"
        f"This reminder will stop automatically when you complete the task.\n\n"
        f"Smart Student Reminder System"
    )
    return _send_email(to_email, subject, body)


