import pytest
from app.services.game import GameService
from app.services.user import UserService
from app.models import Game, User
from datetime import datetime


def get_game_data(user_data):
    return {
        Game.CREATOR: user_data[User.ID]
    }


class TestGameService:
    """Tests for GameService class."""
    def test_create_game_success(self, app_context):
        """Test successful game creation."""
        # First create a user (game needs a creator)
        user_service = UserService()
        user_data = user_service.create_user({"alias": "testuser", "password": "password123"})
        
        # Create game
        game_data = get_game_data(user_data)
        service = GameService()
        result = service.create_game(game_data)
        
        assert result is not None
        assert result[Game.CREATOR] == game_data[Game.CREATOR]
        assert result[Game.ID] == 1
        assert result[Game.STARTED_AT] is not None
        assert result[Game.ENDED_AT] is None

    
    def test_update_game_success(self, app_context):
        """Test updating a game."""
        user_service = UserService()
        user_data = user_service.create_user({"alias": "testuser", "password": "password123"})
        
        service = GameService()
        game_data = get_game_data(user_data)
        game = service.create_game(game_data)
        
        # Update game
        update_data = {"ended_at": datetime.now()}
        result = service.update_game(game[Game.ID], update_data)
        
        assert result is not None
        assert result[Game.ENDED_AT] is not None


    def test_delete_game_success(self, app_context):
        """Test deleting a game."""
        user_service = UserService()
        user_data = user_service.create_user({"alias": "testuser", "password": "password123"})
        
        service = GameService()
        game_data = get_game_data(user_data)
        game = service.create_game(game_data)
        
        # Delete game
        result = service.delete_game(game[Game.ID])
        assert result is True


class TestGameRoutes:
    """Tests for game API routes."""
    def test_create_game_route_success(self, client):
        """Test POST /games endpoint success."""
        response = client.post("/games", json={})
        assert response.status_code == 201
        assert response.get_json()[Game.CREATOR] is not None
    

    def test_update_game_route_success(self, client):
        """Test PUT /games/<id> endpoint success."""
        create_response = client.post("/games", json={})
        game_id = create_response.get_json()[Game.ID]
        
        # Update game
        update_data = {"ended_at": datetime.now().isoformat()}
        response = client.put(f"/games/{game_id}", json=update_data)
        assert response.status_code == 200
    

    def test_delete_game_route_success(self, client):
        """Test DELETE /games/<id> endpoint success."""
        create_response = client.post("/games", json={})
        game_id = create_response.get_json()[Game.ID]
        
        # Delete game
        response = client.delete(f"/games/{game_id}")
        assert response.status_code == 204


    def test_create_game_route_invalid_data(self, client):
        """Test POST /games with invalid data payload still uses token user."""
        response = client.post("/games", json={})
        assert response.status_code == 201


    def test_create_game_route_rejects_active_game(self, client):
        """Test POST /games when authenticated user already has an active game."""
        first_response = client.post("/games", json={})
        assert first_response.status_code == 201

        response = client.post("/games", json={})
        assert response.status_code == 400
        assert response.get_json()["error"] == "Creator already has an active game"