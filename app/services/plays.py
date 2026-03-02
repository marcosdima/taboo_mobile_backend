from app.extensions import db
from app.models import Plays, Game


class PlaysService:
    def add_play(self, data):
        """Add a new play record (user playing in a game)"""
        user_id = data.get("user_id")
        game_id = data.get("game_id")

        if not user_id or not game_id:
            raise ValueError("User ID and Game ID are required")

        # Check if play already exists
        existing_play = Plays.query.filter_by(user_id=user_id, game_id=game_id).first()
        if existing_play:
            raise ValueError("User already playing in this game")
        
        # Check if game exists and is active.
        game = Game.query.get(game_id)

        play = Plays(user_id=user_id, game_id=game_id)
        db.session.add(play)
        db.session.commit()

        return play.to_dict()


    def delete_play(self, user_id, game_id):
        """Remove a play record"""
        play = Plays.query.filter_by(user_id=user_id, game_id=game_id).first()
        if play:
            db.session.delete(play)
            db.session.commit()
            return True
        return False


    def get_plays_by_game(self, game_id):
        """Get all plays in a game"""
        plays = Plays.query.filter_by(game_id=game_id).all()
        return [play.to_dict() for play in plays]


    def delete_current_plays(self, user_id):
        """Delete current play with active game"""
        curr = self.get_current_play(user_id)
        if curr:
            self.delete_play(user_id, curr[Plays.GAME_ID])
            return True
        return False


    def get_all_plays(self):
        """Get all plays"""
        plays = Plays.query.all()
        return [play.to_dict() for play in plays]
    

    def get_current_play(self, user_id):
        """Get current play with active game"""
        play = Plays.query.join(Game).filter(
            Plays.user_id == user_id,
            Game.ended_at.is_(None)
        ).first()
        return play.to_dict() if play else None


    def is_playing(self, user_id):
        """Check if a user is playing in an active game (ended_at is null)"""
        return self.get_current_play(user_id) is not None
