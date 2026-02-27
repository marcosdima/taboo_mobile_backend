from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.extensions import db

class Game(db.Model):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime, nullable=True)
    creator = Column(Integer, ForeignKey('users.id')) 


    def __repr__(self):
        return f"<Game(id={self.id}>"