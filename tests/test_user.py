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
    def test_create_user_success(self, app_context, user_data):
        """ Test successful user creation. """
        service = UserService()
        result = service.create_user(user_data)
        
        assert result is not None
        assert result[User.ALIAS] == user_data[User.ALIAS]
        assert result[User.ID] == 1

    
    def test_create_user_duplicate_alias(self, app_context, user_data):
        """ Test user creation with duplicate alias. """
        service = UserService()
        service.create_user(user_data)
        with pytest.raises(Exception):
            service.create_user(user_data)

    
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
    

    def test_create_user_route_invalid_data(self, client):
        """Test POST /users with invalid data."""
        response = client.post("/users", json={})
        assert response.status_code == 400
    

    def test_get_users_route(self, client, user_data):
        """Test GET /users endpoint."""
        response = client.get("/users")

        # User does not exist yet, so we expect an empty list.
        assert response.status_code == 200
        assert response.get_json() == []
        
        # Create a user and test again.
        client.post("/users", json=user_data)
        response = client.get("/users")
        assert response.status_code == 200
        assert len(response.get_json()) == 1
        