import pytest
from app import create_app
from database.db_config import db
from models import User

from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        # Seed test admin
        admin = User(email="admin@test.com", full_name="Test Admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_redirect_unauthenticated(client):
    """Test that unauthenticated requests redirect to login."""
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Please log in to access this page" in response.data

def test_login_success(client):
    """Test standard admin login success."""
    response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow_redirects=True)
    assert b"Welcome back" in response.data
    assert b"System Administration Overview" in response.data

def test_role_guard_restriction(client):
    """Test that authenticated users cannot access unauthorized role views."""
    # Login as admin
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    # Attempt to access student view
    response = client.get('/student/dashboard', follow_redirects=True)
    assert b"Access denied" in response.data
