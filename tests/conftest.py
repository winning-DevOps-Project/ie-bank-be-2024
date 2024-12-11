from iebank_api import create_app, db
from iebank_api.models import User, Account
import pytest

@pytest.fixture
def app():
    """
    Create and configure a new app instance for each test.
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test_secret'  # Test JWT secret

    with app.app_context():
        db.create_all()  # Create database tables for the test
        yield app  # This provides the app to the tests

        # Clean up / drop the database
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """
    A test client for the app.
    """
    return app.test_client()

@pytest.fixture
def create_user(app):
    """Fixture to create a test user."""
    with app.app_context():
        user = User(username='testuser', is_admin=True)
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
    return user

@pytest.fixture
def create_account(app, create_user):
    """Fixture to create a test account."""
    with app.app_context():
        account = Account(
            name="Test Account",
            currency="€",
            country="Spain",
        )
        db.session.add(account)
        db.session.commit()