from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.extensions import db

class Group(db.Model):
    __tablename__ = 'groups'
    __table_args__ = (
        UniqueConstraint('name', 'game_id', name='unique_group_name_game'),
        UniqueConstraint('id', 'game_id', name='unique_group_id_game'),
    )

    ID = 'id'
    NAME = 'name'
    GAME = 'game_id'


    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    name = Column(String(255), nullable=False)


    def to_dict(self):
        return {
            self.ID: self.id,
            self.NAME: self.name,
            self.GAME: self.game_id,
        }


    def __repr__(self):
        return f"<Group({self.name})>"