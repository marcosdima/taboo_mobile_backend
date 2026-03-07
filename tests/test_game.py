import pytest
from app.services.game import GameService
from app.services.user import UserService
from app.models import Game, User, Group
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
        assert result[Game.ID] is not None
        assert result[Game.STARTED_AT] is not None
        assert result[Game.ENDED_AT] is None

        groups = Group.query.filter_by(game_id=result[Game.ID]).all()
        assert sorted([group.name for group in groups]) == ["Blue", "Red"]

    
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

    @staticmethod
    def _auth_headers_for(client, alias, password="password123"):
        login_response = client.post("/login", json={"alias": alias, "password": password})
        token = login_response.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}


    def test_create_game_route_success(self, client):
        """Test POST /games endpoint success."""
        response = client.post("/games", json={})
        assert response.status_code == 201
        payload = response.get_json()
        assert payload[Game.CREATOR] is not None

        groups_response = client.get(f"/groups/{payload[Game.ID]}")
        assert groups_response.status_code == 200
        assert sorted([group["name"] for group in groups_response.get_json()]) == ["Blue", "Red"]
    

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


    def test_update_game_route_fails_for_non_creator(self, client):
        create_response = client.post("/games", json={})
        game_id = create_response.get_json()[Game.ID]

        client.post("/users", json={"alias": "outsider_updater", "password": "password123"})
        outsider_headers = self._auth_headers_for(client, "outsider_updater")

        response = client.put(
            f"/games/{game_id}",
            json={"ended_at": datetime.now().isoformat()},
            headers=outsider_headers,
        )

        assert response.status_code == 403
        assert response.get_json()["error"] == "Only game creator can perform this action"


    def test_delete_game_route_fails_for_non_creator(self, client):
        create_response = client.post("/games", json={})
        game_id = create_response.get_json()[Game.ID]

        client.post("/users", json={"alias": "outsider_deleter", "password": "password123"})
        outsider_headers = self._auth_headers_for(client, "outsider_deleter")

        response = client.delete(f"/games/{game_id}", headers=outsider_headers)

        assert response.status_code == 403
        assert response.get_json()["error"] == "Only game creator can perform this action"


    def test_start_game_route_success(self, client):
        create_response = client.post("/games", json={})
        game_id = create_response.get_json()[Game.ID]

        client.post("/users", json={"alias": "second_player", "password": "password123"})
        second_player_headers = self._auth_headers_for(client, "second_player")

        join_response = client.post(
            "/play",
            json={"game_id": game_id},
            headers=second_player_headers,
        )
        assert join_response.status_code == 201

        response = client.post("/games/start", json={})

        assert response.status_code == 200
        payload = response.get_json()
        assert payload[Game.ID] == game_id
        assert payload[Game.ENDED_AT] is None


    def test_start_game_route_rejects_when_user_has_no_active_game(self, client):
        client.post("/users", json={"alias": "no_active_game_user", "password": "password123"})
        no_game_headers = self._auth_headers_for(client, "no_active_game_user")

        response = client.post("/games/start", json={}, headers=no_game_headers)

        assert response.status_code == 400
        assert response.get_json()["error"] == "User has no active game"


    def test_start_game_route_rejects_when_user_is_not_creator(self, client):
        create_response = client.post("/games", json={})
        game_id = create_response.get_json()[Game.ID]

        client.post("/users", json={"alias": "non_creator_player", "password": "password123"})
        non_creator_headers = self._auth_headers_for(client, "non_creator_player")

        join_response = client.post(
            "/play",
            json={"game_id": game_id},
            headers=non_creator_headers,
        )
        assert join_response.status_code == 201

        response = client.post("/games/start", json={}, headers=non_creator_headers)

        assert response.status_code == 403
        assert response.get_json()["error"] == "Only game creator can start the game"