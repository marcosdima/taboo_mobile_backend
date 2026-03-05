import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User, Game, Plays, Group, Member


def create_user(alias: str) -> User:
    user = User(alias=alias)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def create_game(creator_id: int) -> Game:
    game = Game(creator=creator_id)
    db.session.add(game)
    db.session.commit()
    return game


def create_play(user_id: int, game_id: int) -> Plays:
    play = Plays(user_id=user_id, game_id=game_id)
    db.session.add(play)
    db.session.commit()
    return play


def create_group(game_id: int, name: str) -> Group:
    group = Group(game_id=game_id, name=name)
    db.session.add(group)
    db.session.commit()
    return group


class TestMemberModel:
    def test_create_member_success(self, app_context):
        user = create_user("member_user")
        game = create_game(user.id)
        play = create_play(user.id, game.id)
        group = create_group(game.id, "Team A")

        member = Member(play_id=play.id, group_id=group.id, game_id=game.id)
        db.session.add(member)
        db.session.commit()

        assert member.id is not None
        assert member.play_id == play.id
        assert member.group_id == group.id
        assert member.game_id == game.id

    def test_play_can_only_belong_to_one_member(self, app_context):
        user1 = create_user("member_user_1")
        user2 = create_user("member_user_2")
        game = create_game(user1.id)

        play1 = create_play(user1.id, game.id)
        create_play(user2.id, game.id)

        group1 = create_group(game.id, "Team 1")
        group2 = create_group(game.id, "Team 2")

        member1 = Member(play_id=play1.id, group_id=group1.id, game_id=game.id)
        db.session.add(member1)
        db.session.commit()

        duplicated_member = Member(play_id=play1.id, group_id=group2.id, game_id=game.id)
        db.session.add(duplicated_member)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    def test_play_and_group_must_belong_to_same_game(self, app_context):
        user = create_user("member_user_mismatch")
        game1 = create_game(user.id)

        other_user = create_user("member_user_other")
        game2 = create_game(other_user.id)

        play = create_play(user.id, game1.id)
        group = create_group(game2.id, "Foreign Team")

        with pytest.raises(ValueError, match="Member.game_id must match Group.game_id"):
            Member(play_id=play.id, group_id=group.id, game_id=game1.id)
