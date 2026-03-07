import pytest
from unittest.mock import Mock
from app.services.user import UserService
from app.models import User


@pytest.fixture
def user_data():
    """Fixture providing sample user data."""
    return {
        "alias": "testuser",
        "password": "securepassword123"
    }


class TestUserService:
    """Tests for UserService class."""
    def test_password_hash_column_length(self):
        """Ensure password_hash column is large enough for modern hash strings."""
        assert User.__table__.c.password_hash.type.length == 255

    def test_create_user_success(self, app_context, user_data):
        """ Test successful user creation. """
        service = UserService()
        result = service.create_user(user_data)
        
        assert result is not None
        assert result[User.ALIAS] == user_data[User.ALIAS]
        assert result[User.ID] == 1

    
    def test_get_user_by_alias(self, app_context, user_data):
        """ Test alias lookup helper used by route validation. """
        service = UserService()
        created = service.create_user(user_data)

        found = service.get_user_by_alias(user_data[User.ALIAS])
        missing = service.get_user_by_alias("unknown_alias")

        assert found is not None
        assert found[User.ID] == created[User.ID]
        assert missing is None

    
    def test_exists_user(self, app_context, user_data):
        """ Test user existence check. """
        service = UserService()
        user = service.create_user(user_data)
        
        assert service.user_exists(user[User.ID]) is True
        assert service.user_exists(999) is False


class TestUserRoutes:
    """Tests for user API routes."""
    def test_create_user_route_success(self, client, user_data):
        """Test POST /users endpoint success."""
        response = client.post("/users", json=user_data)
        assert response.status_code == 201
        payload = response.get_json()
        assert payload["alias"] == user_data["alias"]
        assert payload["id"] is not None
    

    def test_create_user_route_invalid_data(self, client):
        """Test POST /users with invalid data."""
        response = client.post("/users", json={})
        assert response.status_code == 400
        assert response.get_json()["error"] == "Alias and password required"


    def test_create_user_route_duplicate_alias(self, client, user_data):
        first = client.post("/users", json=user_data)
        assert first.status_code == 201

        duplicate = client.post("/users", json=user_data)
        assert duplicate.status_code == 400
        assert duplicate.get_json()["error"] == "Alias already exists"
    

    def test_get_users_route(self, client, user_data):
        """Test GET /users endpoint."""
        response = client.get("/users")

        # Auth fixture creates one user for obtaining a token.
        assert response.status_code == 200
        assert len(response.get_json()) == 1
        
        # Create a user and test again.
        client.post("/users", json=user_data)
        response = client.get("/users")
        assert response.status_code == 200
        assert len(response.get_json()) == 2
        