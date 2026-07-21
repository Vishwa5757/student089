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

    def __repr__(self):
        return f'<TaskStatus Task:{self.task_id} Student:{self.student_id} Status:{self.status}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Notification User:{self.user_id} Read:{self.is_read}>'
