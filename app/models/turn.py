from sqlalchemy import Column, DateTime, ForeignKey, Integer

from app.extensions import db


class Turn(db.Model):
    __tablename__ = "turns"


    ID = "id"
    GAME_ID = "game_id"
    PLAYER_ID = "player_id"
    STARTED_AT = "started_at"
    ENDS_AT = "ends_at"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("plays.id"), nullable=False)
    started_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)


    def to_dict(self):
        return {
            self.ID: self.id,
            self.GAME_ID: self.game_id,
            self.PLAYER_ID: self.player_id,
            self.STARTED_AT: self.started_at.isoformat() if self.started_at else None,
            self.ENDS_AT: self.ends_at.isoformat() if self.ends_at else None,
        }


    def __repr__(self):
        return (
            f"<Turn(id={self.id}, game_id={self.game_id}, player_id={self.player_id}, "
            f"started_at={self.started_at}, ends_at={self.ends_at})>"
        )

