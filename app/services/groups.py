from app.extensions import db
from app.models import Group, Member, Plays, Game


class GroupsService:
    def _get_active_play(self, user_id, game_id):
        return Plays.query.join(Game).filter(
            Plays.user_id == user_id,
            Plays.game_id == game_id,
            Game.ended_at.is_(None),
        ).first()


    def create_default_groups(self, game_id):
        existing_names = {
            group.name
            for group in Group.query.filter_by(game_id=game_id).all()
            if group.name in {"Red", "Blue"}
        }

        to_create = []
        if "Red" not in existing_names:
            to_create.append(Group(game_id=game_id, name="Red"))
        if "Blue" not in existing_names:
            to_create.append(Group(game_id=game_id, name="Blue"))

        if to_create:
            db.session.add_all(to_create)
            db.session.commit()


    def assign_user_to_group(self, requester_id, user_id, group_id):
        if not user_id or not group_id:
            raise ValueError("user_id and group_id are required")

        group = db.session.get(Group, group_id)
        if not group:
            raise LookupError("Group not found")

        requester_play = self._get_active_play(requester_id, group.game_id)
        if not requester_play:
            raise PermissionError("Only players in this game can assign groups")

        target_play = self._get_active_play(user_id, group.game_id)
        if not target_play:
            raise ValueError("User must be playing in this game")

        existing_member = Member.query.filter_by(play_id=target_play.id).first()
        if existing_member:
            raise ValueError("User already assigned in this game. Use PUT to update")

        member = Member(play_id=target_play.id, group_id=group.id)
        db.session.add(member)
        db.session.commit()

        return member.to_dict()


    def reassign_user_group(self, requester_id, user_id, group_id):
        if not user_id or not group_id:
            raise ValueError("user_id and group_id are required")

        group = db.session.get(Group, group_id)
        if not group:
            raise LookupError("Group not found")

        game = db.session.get(Game, group.game_id)
        if not game or game.ended_at is not None:
            raise ValueError("Game does not exist or is not active")

        if requester_id != game.creator:
            raise PermissionError("Only game creator can reassign groups")

        target_play = self._get_active_play(user_id, group.game_id)
        if not target_play:
            raise ValueError("User must be playing in this game")

        member = Member.query.filter_by(play_id=target_play.id).first()
        if not member:
            raise LookupError("User has no group assignment in this game")

        member.group_id = group.id
        db.session.commit()

        return member.to_dict()


    def get_groups_by_game(self, game_id):
        game = db.session.get(Game, game_id)
        if not game:
            raise LookupError("Game not found")

        groups = Group.query.filter_by(game_id=game_id).all()
        result = []

        for group in groups:
            group_data = group.to_dict()
            members = Member.query.filter_by(group_id=group.id).all()
            group_data["members"] = [member.to_dict() for member in members]
            result.append(group_data)

        return result
