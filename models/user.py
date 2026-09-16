from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'professor', 'student', name='user_roles'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    created_tasks = db.relationship('Task', backref='professor', lazy=True, cascade='all, delete-orphan')
    assigned_tasks = db.relationship('TaskStatus', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, plaintext_password):
        """Hashes the password securely."""
        self.password = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        """Verifies plaintext password against the stored hash."""
        return check_password_hash(self.password, plaintext_password)

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"
