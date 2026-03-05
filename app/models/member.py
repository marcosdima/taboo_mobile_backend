from sqlalchemy import Column, Integer, ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, validates

from app.extensions import db
from app.models.group import Group
from app.models.plays import Plays


class Member(db.Model):
    __tablename__ = 'members'
    __table_args__ = (
        UniqueConstraint('play_id', name='unique_member_play'),
        ForeignKeyConstraint(
            ['play_id', 'game_id'],
            ['plays.id', 'plays.game_id'],
            name='fk_members_play_game_plays'
        ),
        ForeignKeyConstraint(
            ['group_id', 'game_id'],
            ['groups.id', 'groups.game_id'],
            name='fk_members_group_game_groups'
        ),
    )


    ID = 'id'
    PLAY_ID = 'play_id'
    GROUP_ID = 'group_id'
    GAME_ID = 'game_id'

    id = Column(Integer, primary_key=True, index=True)
    play_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)

    play = relationship('Plays', uselist=False)
    group = relationship('Group')


    @validates('play_id', 'group_id', 'game_id')
    def validate_game_consistency(self, key, value):
        next_play_id = value if key == 'play_id' else self.play_id
        next_group_id = value if key == 'group_id' else self.group_id
        next_game_id = value if key == 'game_id' else self.game_id

        if next_play_id is not None and next_group_id is not None and next_game_id is not None:
            play = db.session.get(Plays, next_play_id)
            group = db.session.get(Group, next_group_id)

            if play is not None and play.game_id != next_game_id:
                raise ValueError('Member.game_id must match Plays.game_id')

            if group is not None and group.game_id != next_game_id:
                raise ValueError('Member.game_id must match Group.game_id')

        return value


    def to_dict(self):
        return {
            self.ID: self.id,
            self.PLAY_ID: self.play_id,
            self.GROUP_ID: self.group_id,
            self.GAME_ID: self.game_id,
        }


    def __repr__(self):
        return f"<Member(id={self.id}, play_id={self.play_id}, group_id={self.group_id}, game_id={self.game_id})>"
