import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope="module")
def app():
    app = create_app(test_config={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
    return app


@pytest.fixture
def app_context(app):
    """Fixture that provides an active app context for each test."""
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_context):
    """Fixture providing a test client."""
    return app_context.test_client()