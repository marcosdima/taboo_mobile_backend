from app.models import Game, Plays
from app.extensions import db
from datetime import datetime
from .plays import PlaysService
from .groups import GroupsService

class GameService:
    MIN_PLAYERS_TO_START = 2
    MAX_PLAYS_PER_GAME = Game.MAX_PLAYS_PER_GAME


    def get_game_by_id(self, game_id):
        game = db.session.get(Game, game_id)
        return game.to_dict() if game else None


    def create_game(self, data):
        creator_id = data.get(Game.CREATOR)
        
        new_game = Game(**data)
        db.session.add(new_game)
        db.session.commit()

        # If game was created successfully, add the creator as a player in the game.
        plays_service = PlaysService()
        plays_service.add_play({
            Plays.USER_ID: creator_id,
            Plays.GAME_ID: new_game.id
        })

        groups_service = GroupsService()
        groups_service.create_default_groups(new_game.id)
        
        return new_game.to_dict()


    def update_game(self, game_id, data):
        game = db.session.get(Game, game_id)

        if not game:
            return None
        for key, value in data.items():
            # Parse ISO format strings to datetime objects
            if key in ['ended_at', 'started_at'] and isinstance(value, str):
                value = datetime.fromisoformat(value)
            setattr(game, key, value)
            
        db.session.commit()
        return game.to_dict()


    def delete_game(self, game_id):
        game = db.session.get(Game, game_id)
        if game:
            db.session.delete(game)
            db.session.commit()
            return True
        return False
    

    def get_all(self):
        games = Game.query.all()
        return [game.to_dict() for game in games]
    

    def get_active_games(self):
        games = Game.query.filter_by(ended_at=None).all()
        return [game.to_dict() for game in games]


    def end_game(self, game_id):
        return self.update_game(game_id, {Game.ENDED_AT: datetime.now()})


    def start_game(self, game_id):
        return self.update_game(game_id, {Game.STARTED_AT: datetime.now()})
    
