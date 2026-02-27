import pytest
from sqlalchemy.exc import IntegrityError
from app.services.plays import PlaysService
from app.services.game import GameService
from app.services.user import UserService
from app.models import Plays, Game, User


def create_user(alias, password):
    """Helper function to create a user."""
    user_service = UserService()
    return user_service.create_user({"alias": alias, "password": password})


def create_game(creator_id):
    """Helper function to create a game."""
    game_service = GameService()
    return game_service.create_game({Game.CREATOR: creator_id})


class TestPlaysService:
    """Tests for PlaysService class."""
    
    def test_add_play_success(self, app_context):
        """Test successful play addition - creator is added automatically to game."""
        user = create_user("testuser", "password123")
        game = create_game(user[User.ID])
        
        service = PlaysService()
        plays = service.get_plays_by_game(game[Game.ID])
        
        assert len(plays) == 1
        assert plays[0][Plays.USER_ID] == user[User.ID]
        assert plays[0][Plays.GAME_ID] == game[Game.ID]

    
    def test_add_play_another_user(self, app_context):
        """Test adding another user to a game that already has the creator."""
        user1 = create_user("user1", "password123")
        game = create_game(user1[User.ID])
        
        user2 = create_user("user2", "password123")
        service = PlaysService()
        result = service.add_play({
            Plays.USER_ID: user2[User.ID],
            Plays.GAME_ID: game[Game.ID]
        })
        
        plays = service.get_plays_by_game(game[Game.ID])
        assert len(plays) == 2
        user_ids = [p[Plays.USER_ID] for p in plays]
        assert user1[User.ID] in user_ids
        assert user2[User.ID] in user_ids

    
    def test_add_play_multiple_users(self, app_context):
        """Test multiple users joining the same game."""
        user1 = create_user("user1", "password123")
        game = create_game(user1[User.ID])
        user2 = create_user("user2", "password123")
        user3 = create_user("user3", "password123")
        
        service = PlaysService()
        play2 = service.add_play({
            Plays.USER_ID: user2[User.ID],
            Plays.GAME_ID: game[Game.ID]
        })
        
        play3 = service.add_play({
            Plays.USER_ID: user3[User.ID],
            Plays.GAME_ID: game[Game.ID]
        })
        
        assert play2[Plays.USER_ID] == user2[User.ID]
        assert play3[Plays.USER_ID] == user3[User.ID]
        assert play2[Plays.GAME_ID] == play3[Plays.GAME_ID]
        
        plays = service.get_plays_by_game(game[Game.ID])
        assert len(plays) == 3

    
    def test_add_play_duplicate_fails(self, app_context):
        """Test that same user cannot play twice in same game (constraint violation)."""
        user1 = create_user("user1", "password123")
        user2 = create_user("user2", "password123")
        game = create_game(user1[User.ID])
        
        service = PlaysService()
        service.add_play({
            Plays.USER_ID: user2[User.ID],
            Plays.GAME_ID: game[Game.ID]
        })
        
        with pytest.raises(ValueError, match="User already playing in this game"):
            service.add_play({
                Plays.USER_ID: user2[User.ID],
                Plays.GAME_ID: game[Game.ID]
            })

    
    def test_add_play_missing_data(self, app_context):
        """Test play addition with missing required data."""
        service = PlaysService()
        
        # Missing user_id
        with pytest.raises(ValueError, match="User ID and Game ID are required"):
            service.add_play({Plays.GAME_ID: 1})
        
        # Missing game_id
        with pytest.raises(ValueError, match="User ID and Game ID are required"):
            service.add_play({Plays.USER_ID: 1})

    
    def test_delete_play_success(self, app_context):
        """Test successful play deletion."""
        user = create_user("testuser", "password123")
        game = create_game(user[User.ID])
        
        service = PlaysService()
        result = service.delete_play(user[User.ID], game[Game.ID])
        assert result is True

    
    def test_delete_play_not_found(self, app_context):
        """Test deleting a non-existent play."""
        service = PlaysService()
        result = service.delete_play(999, 999)
        assert result is False

    
    def test_get_plays_by_game(self, app_context):
        """Test getting all players in a game."""
        user1 = create_user("user1", "password123")
        game = create_game(user1[User.ID])
        user2 = create_user("user2", "password123")
        user3 = create_user("user3", "password123")
        
        service = PlaysService()
        service.add_play({Plays.USER_ID: user2[User.ID], Plays.GAME_ID: game[Game.ID]})
        service.add_play({Plays.USER_ID: user3[User.ID], Plays.GAME_ID: game[Game.ID]})
        
        plays = service.get_plays_by_game(game[Game.ID])
        assert len(plays) == 3
        assert all(p[Plays.GAME_ID] == game[Game.ID] for p in plays)

    
    def test_get_plays_by_user(self, app_context):
        """Test getting all games where a user plays."""
        user = create_user("testuser", "password123")
        game1 = create_game(user[User.ID])
        user2 = create_user("user2", "password123")
        game2 = create_game(user2[User.ID])
        
        service = PlaysService()
        service.add_play({Plays.USER_ID: user[User.ID], Plays.GAME_ID: game2[Game.ID]})
        
        plays = service.get_plays_by_user(user[User.ID])
        assert len(plays) == 2
        assert all(p[Plays.USER_ID] == user[User.ID] for p in plays)

    
    def test_get_all_plays(self, app_context):
        """Test getting all plays."""
        user1 = create_user("user1", "password123")
        user2 = create_user("user2", "password123")
        game1 = create_game(user1[User.ID])
        game2 = create_game(user2[User.ID])
        
        service = PlaysService()
        service.add_play({Plays.USER_ID: user1[User.ID], Plays.GAME_ID: game2[Game.ID]})
        
        plays = service.get_all_plays()
        assert len(plays) == 3


class TestPlaysRoutes:
    """Tests for plays API routes."""
    
    def test_add_play_route_success(self, client):
        """Test POST /plays endpoint success."""
        # Create users and game
        user1_response = client.post("/users", json={"alias": "user1", "password": "password123"})
        user1_data = user1_response.get_json()
        
        user2_response = client.post("/users", json={"alias": "user2", "password": "password123"})
        user2_data = user2_response.get_json()
        
        game_response = client.post("/games", json={Game.CREATOR: user1_data[User.ID]})
        game_data = game_response.get_json()
        
        # Add user2 to game (user1 already added as creator)
        response = client.post("/plays", json={
            Plays.USER_ID: user2_data[User.ID],
            Plays.GAME_ID: game_data[Game.ID]
        })
        
        assert response.status_code == 201
        assert response.get_json()[Plays.USER_ID] == user2_data[User.ID]

    
    def test_add_play_route_duplicate(self, client):
        """Test POST /plays with duplicate play."""
        # Create users and game
        user1_response = client.post("/users", json={"alias": "user1", "password": "password123"})
        user1_data = user1_response.get_json()
        
        user2_response = client.post("/users", json={"alias": "user2", "password": "password123"})
        user2_data = user2_response.get_json()
        
        game_response = client.post("/games", json={Game.CREATOR: user1_data[User.ID]})
        game_data = game_response.get_json()
        
        # Add user2 to game
        client.post("/plays", json={
            Plays.USER_ID: user2_data[User.ID],
            Plays.GAME_ID: game_data[Game.ID]
        })
        
        # Try to add user2 again
        response = client.post("/plays", json={
            Plays.USER_ID: user2_data[User.ID],
            Plays.GAME_ID: game_data[Game.ID]
        })
        
        assert response.status_code == 400

    
    def test_delete_play_route_success(self, client):
        """Test DELETE /plays/<user_id>/<game_id> endpoint success."""
        # Create users and game
        user1_response = client.post("/users", json={"alias": "user1", "password": "password123"})
        user1_data = user1_response.get_json()
        
        user2_response = client.post("/users", json={"alias": "user2", "password": "password123"})
        user2_data = user2_response.get_json()
        
        game_response = client.post("/games", json={Game.CREATOR: user1_data[User.ID]})
        game_data = game_response.get_json()
        
        # Add user2 to game
        client.post("/plays", json={
            Plays.USER_ID: user2_data[User.ID],
            Plays.GAME_ID: game_data[Game.ID]
        })
        
        # Delete user2's play
        response = client.delete(f"/plays/{user2_data[User.ID]}/{game_data[Game.ID]}")
        assert response.status_code == 204

    
    def test_delete_play_route_not_found(self, client):
        """Test DELETE /plays with non-existent play."""
        response = client.delete("/plays/999/999")
        assert response.status_code == 404

    
    def test_get_plays_by_game_route(self, client):
        """Test GET /plays/game/<game_id> endpoint."""
        # Create users and game 
        user1_response = client.post("/users", json={"alias": "user1", "password": "password123"})
        user1_data = user1_response.get_json()
        
        user2_response = client.post("/users", json={"alias": "user2", "password": "password123"})
        user2_data = user2_response.get_json()
        
        game_response = client.post("/games", json={Game.CREATOR: user1_data[User.ID]})
        game_data = game_response.get_json()
        
        # Add user2 to game (user1 already added as creator)
        client.post("/plays", json={Plays.USER_ID: user2_data[User.ID], Plays.GAME_ID: game_data[Game.ID]})
        
        # Get plays for game
        response = client.get(f"/plays/game/{game_data[Game.ID]}")
        assert response.status_code == 200
        plays = response.get_json()
        assert len(plays) == 2

    
    def test_get_plays_by_user_route(self, client):
        """Test GET /plays/user/<user_id> endpoint."""
        # Create users and games (automatically added as creators)
        user1_response = client.post("/users", json={"alias": "user1", "password": "password123"})
        user1_data = user1_response.get_json()
        
        user2_response = client.post("/users", json={"alias": "user2", "password": "password123"})
        user2_data = user2_response.get_json()
        
        game1_response = client.post("/games", json={Game.CREATOR: user1_data[User.ID]})
        game1_data = game1_response.get_json()
        
        game2_response = client.post("/games", json={Game.CREATOR: user2_data[User.ID]})
        game2_data = game2_response.get_json()
        
        # User1 plays in game2 (already in game1 as creator)
        client.post("/plays", json={Plays.USER_ID: user1_data[User.ID], Plays.GAME_ID: game2_data[Game.ID]})
        
        # Get plays for user1
        response = client.get(f"/plays/user/{user1_data[User.ID]}")
        assert response.status_code == 200
        plays = response.get_json()
        assert len(plays) == 2

    
    def test_get_all_plays_route(self, client):
        """Test GET /plays endpoint."""
        # Create users and games (user1 automatically added as creator)
        user1_response = client.post("/users", json={"alias": "user1", "password": "password123"})
        user1_data = user1_response.get_json()
        
        user2_response = client.post("/users", json={"alias": "user2", "password": "password123"})
        user2_data = user2_response.get_json()
        
        game_response = client.post("/games", json={Game.CREATOR: user1_data[User.ID]})
        game_data = game_response.get_json()
        
        # Add user2 to game (user1 already added as creator)
        client.post("/plays", json={Plays.USER_ID: user2_data[User.ID], Plays.GAME_ID: game_data[Game.ID]})
        
        # Get all plays
        response = client.get("/plays")
        assert response.status_code == 200
        plays = response.get_json()
        assert len(plays) == 2
