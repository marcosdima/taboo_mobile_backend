from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import validates

from app.extensions import db
from app.models.group import Group
from app.models.plays import Plays


class Member(db.Model):
    __tablename__ = 'members'
    __table_args__ = (UniqueConstraint('play_id', name='unique_member_play'),)


    ID = 'id'
    PLAY_ID = 'play_id'
    GROUP_ID = 'group_id'

    id = Column(Integer, primary_key=True, index=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)

    @validates('play_id', 'group_id')
    def validate_game_consistency(self, key, value):
        next_play_id = value if key == 'play_id' else self.play_id
        next_group_id = value if key == 'group_id' else self.group_id

        if next_play_id is not None and next_group_id is not None:
            play = db.session.get(Plays, next_play_id)
            group = db.session.get(Group, next_group_id)

            if play is not None and group is not None and play.game_id != group.game_id:
                raise ValueError('Plays.game_id must match Group.game_id')

        return value


    def to_dict(self):
        return {
            self.ID: self.id,
            self.PLAY_ID: self.play_id,
            self.GROUP_ID: self.group_id,
        }


    def __repr__(self):
        return f"<Member(id={self.id}, play_id={self.play_id}, group_id={self.group_id})>"
