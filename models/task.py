from datetime import datetime
from models.database import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.Date, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to task status records
    statuses = db.relationship('TaskStatus', backref='task', lazy=True, cascade='all, delete-orphan')

    @property
    def total_assigned(self):
        return len(self.statuses)

    @property
    def completed_count(self):
        return sum(1 for s in self.statuses if s.status == 'Completed')

    @property
    def pending_count(self):
        return sum(1 for s in self.statuses if s.status == 'Pending')

    @property
    def completion_percentage(self):
        if self.total_assigned == 0:
            return 0
        return round((self.completed_count / self.total_assigned) * 100)

    def __repr__(self):
        return f"<Task {self.title}>"


class TaskStatus(db.Model):
    __tablename__ = 'task_status'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Enum('Pending', 'Completed', name='task_status_enum'), nullable=False, default='Pending')
    completed_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('task_id', 'student_id', name='unique_task_student'),
    )

    def __repr__(self):
        return f"<TaskStatus Task:{self.task_id} Student:{self.student_id} Status:{self.status}>"
