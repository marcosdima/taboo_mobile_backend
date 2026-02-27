from app.extensions import db
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class Plays(db.Model):
    __tablename__ = 'plays'


    ID = 'id'
    USER_ID = 'user_id'
    GAME_ID = 'game_id'


    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)


    __table_args__ = (UniqueConstraint('user_id', 'game_id', name='unique_user_game'),)


    def to_dict(self):
        return {
            self.ID: self.id,
            self.USER_ID: self.user_id,
            self.GAME_ID: self.game_id
        }


    def __repr__(self):
        return f"<Plays(id={self.id}, user_id={self.user_id}, game_id={self.game_id})>"
