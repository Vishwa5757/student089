from datetime import datetime
from models.database import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('User', backref=db.backref('notifications', lazy=True, cascade='all, delete-orphan'))
    task = db.relationship('Task', backref=db.backref('notifications', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Notification ID:{self.id} Student:{self.student_id} Read:{self.is_read}>"
