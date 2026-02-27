from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.extensions import db

class Game(db.Model):
    __tablename__ = 'games'


    ID = 'id'
    STARTED_AT = 'started_at'
    ENDED_AT = 'ended_at'
    CREATOR = 'creator'


    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime, nullable=True)
    creator = Column(Integer, ForeignKey('users.id'))


    def to_dict(self):
        return {
            self.ID: self.id,
            self.STARTED_AT: self.started_at.isoformat() if self.started_at else None,
            self.ENDED_AT: self.ended_at.isoformat() if self.ended_at else None,
            self.CREATOR: self.creator
        }


    def __repr__(self):
        return f"<Game(id={self.id}>"