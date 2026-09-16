from datetime import datetime, timezone
from database.db_config import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), default='Medium')  # 'Low', 'Medium', 'High', 'Urgent'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    statuses = db.relationship('TaskStatus', backref='task', lazy=True, cascade='all, delete-orphan')

    @property
    def due_date(self):
        return self.deadline

    @due_date.setter
    def due_date(self, value):
        self.deadline = value

    @property
    def creator(self):
        return self.faculty.user if self.faculty and hasattr(self.faculty, 'user') else None

    @property
    def is_completed(self):
        return all(s.status == 'Completed' for s in self.statuses) if self.statuses else False

    @property
    def completed_at(self):
        if not self.statuses:
            return None
        completed_times = [s.completed_at for s in self.statuses if s.completed_at]
        return max(completed_times) if completed_times else None

    @property
    def assignee(self):
        return self.statuses[0].student.user if self.statuses and self.statuses[0].student else None

    @property
    def last_reminder_sent_at(self):
        if not self.statuses:
            return None
        times = [s.last_reminder_sent_at for s in self.statuses if s.last_reminder_sent_at]
        return max(times) if times else None

    @property
    def reminder_count(self):
        return sum(s.reminder_count or 0 for s in self.statuses) if self.statuses else 0

    @property
    def assignment_notified(self):
        return all(s.assignment_notified for s in self.statuses) if self.statuses else False

    def __repr__(self):
        return f'<Task {self.title}>'


class TaskStatus(db.Model):
    __tablename__ = 'task_status'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Completed'
    completed_at = db.Column(db.DateTime, nullable=True)
    student_remarks = db.Column(db.Text, nullable=True)
    last_reminder_sent_at = db.Column(db.DateTime, nullable=True)
    reminder_count = db.Column(db.Integer, default=0)
    assignment_notified = db.Column(db.Boolean, default=False)

    @property
    def is_completed(self):
        return self.status == 'Completed'

    @is_completed.setter
    def is_completed(self, val):
        self.status = 'Completed' if val else 'Pending'

    @property
    def assignee(self):
        return self.student.user if self.student and hasattr(self.student, 'user') else None

    @property
    def due_date(self):
        return self.task.deadline if self.task else None

    def __repr__(self):
        return f'<TaskStatus Task:{self.task_id} Student:{self.student_id} Status:{self.status}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    notification_type = db.Column(db.String(50), nullable=True)  # 'assignment', 'reminder', 'TASK_ASSIGNED', 'REMINDER_10MIN'
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Notification User:{self.user_id} Type:{self.notification_type} Read:{self.is_read}>'

