from app.models.game import Game
from app.extensions import db

class GameService:
    def create_game(self, data):
        new_game = Game(**data)
        db.session.add(new_game)
        db.session.commit()
        return new_game


    def update_game(self, game_id, data):
        game = Game.query.get(game_id)
        if not game:
            return None
        for key, value in data.items():
            setattr(game, key, value)
        db.session.commit()
        return game


    def delete_game(self, game_id):
        game = Game.query.get(game_id)
        if game:
            db.session.delete(game)
            db.session.commit()