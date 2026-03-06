import random
from collections import Counter
from datetime import datetime, timedelta

from app.extensions import db
from app.models import Game, Group, Member, Plays, Turn


class TurnService:
    TURN_DURATION_SECONDS = 60


    def create_turn(self, game_id):
        # Do not create a new turn if there is already a pending or active one.
        current_turn = self.get_current_turn(game_id)
        if current_turn is not None:
            raise ValueError("Cannot create a turn while another pending or active turn exists")

        # Pick the next player based on turn history and team balancing rules.
        player_id = self.next_player(game_id)
        turn = Turn(game_id=game_id, player_id=player_id)

        # Persist the turn without timing data; timing is set when the turn starts.
        db.session.add(turn)
        db.session.commit()

        return turn.to_dict()


    def start_turn(self, game_id):
        # Reuse a current turn if it exists, otherwise create the next turn.
        current_turn = self.get_current_turn(game_id)
        if current_turn is None:
            created = self.create_turn(game_id)
            current_turn = db.session.get(Turn, created[Turn.ID])

        # Initialize timing only once for the current turn.
        if current_turn.started_at is None:
            now = datetime.now()
            current_turn.started_at = now
            # TODO: Replace fixed turn duration with game configuration model.
            current_turn.ends_at = now + timedelta(seconds=self.TURN_DURATION_SECONDS)
            db.session.commit()

        return current_turn.to_dict()


    def next_player(self, game_id):
        # Turns can only be assigned in active games.
        game = db.session.get(Game, game_id)
        if not game or game.ended_at is not None:
            raise ValueError("Game does not exist or is not active")

        # Load groups and members to apply team-aware balancing.
        groups = Group.query.filter_by(game_id=game_id).all()
        members = []
        if groups:
            group_ids = [group.id for group in groups]
            members = Member.query.filter(Member.group_id.in_(group_ids)).all()

        # Count historical turns per player in this game.
        turns = Turn.query.filter_by(game_id=game_id).all()
        player_turn_counts = Counter(turn.player_id for turn in turns)

        if members:
            # Map each play to its group and count turns per group.
            play_group = {member.play_id: member.group_id for member in members}
            group_turn_counts = Counter(
                play_group[turn.player_id]
                for turn in turns
                if turn.player_id in play_group
            )

            # Pick among groups with the fewest turns.
            candidate_groups = sorted(set(play_group.values()))
            min_group_turns = min(group_turn_counts.get(group_id, 0) for group_id in candidate_groups)
            eligible_groups = [
                group_id
                for group_id in candidate_groups
                if group_turn_counts.get(group_id, 0) == min_group_turns
            ]
            selected_group_id = random.choice(eligible_groups)

            # Inside that group, pick players with the fewest turns.
            candidate_play_ids = [
                play_id for play_id, group_id in play_group.items() if group_id == selected_group_id
            ]
            min_player_turns = min(player_turn_counts.get(play_id, 0) for play_id in candidate_play_ids)
            eligible_players = [
                play_id
                for play_id in candidate_play_ids
                if player_turn_counts.get(play_id, 0) == min_player_turns
            ]

            return random.choice(eligible_players)

        # Fallback when no member assignments exist: pick from all game players.
        candidate_plays = Plays.query.filter_by(game_id=game_id).all()
        if not candidate_plays:
            raise ValueError("No players available for turn in this game")

        candidate_play_ids = [play.id for play in candidate_plays]
        min_turns = min(player_turn_counts.get(play_id, 0) for play_id in candidate_play_ids)
        eligible_players = [
            play_id for play_id in candidate_play_ids if player_turn_counts.get(play_id, 0) == min_turns
        ]
        return random.choice(eligible_players)


    def get_current_turn(self, game_id):
        # The latest turn is considered current if it is pending or active.
        turn = Turn.query.filter_by(game_id=game_id).order_by(Turn.id.desc()).first()
        if not turn:
            return None

        # A turn that exists but has not started yet is still the current turn.
        if turn.started_at is None:
            return turn

        # Once the latest started turn has ended, there is no current turn.
        if self.is_turn_ended(turn):
            return None

        return turn


    def is_turn_ended(self, turn):
        # Missing end time means the turn cannot be considered ended yet.
        if turn is None or turn.ends_at is None:
            return False

        # Turn is ended when now reaches or passes the planned end timestamp.
        return datetime.now() >= turn.ends_at