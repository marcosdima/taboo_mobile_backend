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
    client = app_context.test_client()

    alias = "auth_fixture_user"
    password = "auth_fixture_password"

    client.post("/users", json={"alias": alias, "password": password})
    login_response = client.post("/login", json={"alias": alias, "password": password})
    token = login_response.get_json()["token"]

    original_open = client.open

    def open_with_auth(*args, **kwargs):
        headers = kwargs.pop("headers", {}) or {}
        headers.setdefault("Authorization", f"Bearer {token}")
        kwargs["headers"] = headers
        return original_open(*args, **kwargs)

    client.open = open_with_auth
    return client