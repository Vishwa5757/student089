from database.db_config import db

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    dept_code = db.Column(db.String(20), unique=True, nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)

    # Relationships
    classes = db.relationship('Class', backref='department', lazy=True, cascade='all, delete-orphan')
    faculties = db.relationship('Faculty', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.dept_code} - {self.dept_name}>'


class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    class_code = db.Column(db.String(20), unique=True, nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    # Relationships
    students = db.relationship('Student', backref='class_assigned', lazy=True)
    tasks = db.relationship('Task', backref='class_assigned', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Class {self.class_code}>'


class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    designation = db.Column(db.String(100), default='Professor')

    # Relationships
    tasks = db.relationship('Task', backref='faculty', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Faculty ID {self.id}>'


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    # Relationships
    task_statuses = db.relationship('TaskStatus', backref='student', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Student Roll {self.roll_number}>'
