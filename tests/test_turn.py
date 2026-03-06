from datetime import datetime, timedelta

import pytest

from app.extensions import db
from app.models import Game, Group, Member, Plays, Turn, User
from app.services.turn import TurnService


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


def assign_member(play_id: int, group_id: int) -> Member:
    member = Member(play_id=play_id, group_id=group_id)
    db.session.add(member)
    db.session.commit()
    return member


class TestTurnModel:
    def test_create_turn_success(self, app_context):
        user = create_user("turn_model_user")
        game = create_game(user.id)
        play = create_play(user.id, game.id)

        turn = Turn(game_id=game.id, player_id=play.id)
        db.session.add(turn)
        db.session.commit()

        assert turn.id is not None
        assert turn.game_id == game.id
        assert turn.player_id == play.id


    def test_turn_to_dict(self, app_context):
        user = create_user("turn_dict_user")
        game = create_game(user.id)
        play = create_play(user.id, game.id)

        started_at = datetime.now()
        ends_at = started_at + timedelta(seconds=60)
        turn = Turn(game_id=game.id, player_id=play.id, started_at=started_at, ends_at=ends_at)
        db.session.add(turn)
        db.session.commit()

        payload = turn.to_dict()
        assert payload[Turn.ID] == turn.id
        assert payload[Turn.GAME_ID] == game.id
        assert payload[Turn.PLAYER_ID] == play.id
        assert payload[Turn.STARTED_AT] == started_at.isoformat()
        assert payload[Turn.ENDS_AT] == ends_at.isoformat()


class TestTurnService:
    def test_create_turn_assigns_next_player(self, app_context):
        user = create_user("turn_create_user")
        game = create_game(user.id)
        play = create_play(user.id, game.id)

        service = TurnService()
        payload = service.create_turn(game.id)

        assert payload[Turn.ID] is not None
        assert payload[Turn.GAME_ID] == game.id
        assert payload[Turn.PLAYER_ID] == play.id
        assert payload[Turn.STARTED_AT] is None
        assert payload[Turn.ENDS_AT] is None


    def test_create_turn_fails_if_active_turn_exists(self, app_context):
        user = create_user("turn_active_user")
        game = create_game(user.id)
        create_play(user.id, game.id)

        service = TurnService()
        service.start_turn(game.id)

        with pytest.raises(ValueError, match="Cannot create a turn while another pending or active turn exists"):
            service.create_turn(game.id)


    def test_start_turn_sets_default_duration(self, app_context):
        user = create_user("turn_duration_user")
        game = create_game(user.id)
        create_play(user.id, game.id)

        service = TurnService()
        payload = service.start_turn(game.id)

        started = datetime.fromisoformat(payload[Turn.STARTED_AT])
        ended = datetime.fromisoformat(payload[Turn.ENDS_AT])
        assert int((ended - started).total_seconds()) == TurnService.TURN_DURATION_SECONDS


    def test_get_current_turn_returns_none_when_no_turn(self, app_context):
        user = create_user("turn_empty_user")
        game = create_game(user.id)
        create_play(user.id, game.id)

        service = TurnService()
        assert service.get_current_turn(game.id) is None


    def test_get_current_turn_returns_none_when_ended(self, app_context):
        user = create_user("turn_ended_user")
        game = create_game(user.id)
        play = create_play(user.id, game.id)

        turn = Turn(
            game_id=game.id,
            player_id=play.id,
            started_at=datetime.now() - timedelta(seconds=120),
            ends_at=datetime.now() - timedelta(seconds=60),
        )
        db.session.add(turn)
        db.session.commit()

        service = TurnService()
        assert service.get_current_turn(game.id) is None


    def test_is_turn_ended(self, app_context):
        user = create_user("turn_check_user")
        game = create_game(user.id)
        play = create_play(user.id, game.id)

        ended_turn = Turn(
            game_id=game.id,
            player_id=play.id,
            started_at=datetime.now() - timedelta(seconds=120),
            ends_at=datetime.now() - timedelta(seconds=60),
        )
        active_turn = Turn(
            game_id=game.id,
            player_id=play.id,
            started_at=datetime.now() - timedelta(seconds=10),
            ends_at=datetime.now() + timedelta(seconds=50),
        )
        db.session.add(ended_turn)
        db.session.add(active_turn)
        db.session.commit()

        service = TurnService()
        assert service.is_turn_ended(ended_turn) is True
        assert service.is_turn_ended(active_turn) is False


    def test_next_player_prefers_group_with_fewer_turns(self, app_context):
        creator = create_user("turn_group_creator")
        user_a = create_user("turn_group_user_a")
        user_b = create_user("turn_group_user_b")

        game = create_game(creator.id)
        play_creator = create_play(creator.id, game.id)
        play_a = create_play(user_a.id, game.id)
        play_b = create_play(user_b.id, game.id)

        group_red = create_group(game.id, "Red")
        group_blue = create_group(game.id, "Blue")

        assign_member(play_creator.id, group_red.id)
        assign_member(play_a.id, group_red.id)
        assign_member(play_b.id, group_blue.id)

        db.session.add(Turn(game_id=game.id, player_id=play_creator.id))
        db.session.add(Turn(game_id=game.id, player_id=play_a.id))
        db.session.commit()

        service = TurnService()
        next_player_id = service.next_player(game.id)
        assert next_player_id == play_b.id


    def test_next_player_prefers_least_used_player_inside_group(self, app_context, monkeypatch):
        creator = create_user("turn_inner_creator")
        user_a = create_user("turn_inner_user_a")
        user_b = create_user("turn_inner_user_b")

        game = create_game(creator.id)
        play_creator = create_play(creator.id, game.id)
        play_a = create_play(user_a.id, game.id)
        play_b = create_play(user_b.id, game.id)

        only_group = create_group(game.id, "Only Group")
        assign_member(play_creator.id, only_group.id)
        assign_member(play_a.id, only_group.id)
        assign_member(play_b.id, only_group.id)

        db.session.add(Turn(game_id=game.id, player_id=play_creator.id))
        db.session.add(Turn(game_id=game.id, player_id=play_a.id))
        db.session.commit()

        monkeypatch.setattr("app.services.turn.random.choice", lambda seq: sorted(seq)[0])

        service = TurnService()
        next_player_id = service.next_player(game.id)
        assert next_player_id == play_b.id


    def test_next_player_raises_when_no_players(self, app_context):
        creator = create_user("turn_no_players_creator")
        game = create_game(creator.id)

        service = TurnService()
        with pytest.raises(ValueError, match="No players available for turn in this game"):
            service.next_player(game.id)
