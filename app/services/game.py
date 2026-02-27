from app.models import Game
from app.extensions import db
from datetime import datetime

class GameService:
    def create_game(self, data):
        new_game = Game(**data)
        db.session.add(new_game)
        db.session.commit()
        return new_game.to_dict()


    def update_game(self, game_id, data):
        game = Game.query.get(game_id)
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
        game = Game.query.get(game_id)
        if game:
            db.session.delete(game)
            db.session.commit()
            return True
        return False