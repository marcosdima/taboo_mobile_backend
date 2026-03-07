from app.extensions import db
from app.models import Group, Member, Plays, Game


class GroupsService:
    def _get_active_play(self, user_id, game_id):
        return Plays.query.join(Game).filter(
            Plays.user_id == user_id,
            Plays.game_id == game_id,
            Game.ended_at.is_(None),
        ).first()


    def get_group_by_id(self, group_id):
        group = db.session.get(Group, group_id)
        return group.to_dict() if group else None


    def get_active_play_by_user_and_game(self, user_id, game_id):
        play = self._get_active_play(user_id, game_id)
        return play.to_dict() if play else None


    def get_member_by_play_id(self, play_id):
        member = Member.query.filter_by(play_id=play_id).first()
        return member.to_dict() if member else None


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
        group = db.session.get(Group, group_id)
        target_play = self._get_active_play(user_id, group.game_id)

        member = Member(play_id=target_play.id, group_id=group.id)
        db.session.add(member)
        db.session.commit()

        return member.to_dict()


    def reassign_user_group(self, requester_id, user_id, group_id):
        group = db.session.get(Group, group_id)
        target_play = self._get_active_play(user_id, group.game_id)
        member = Member.query.filter_by(play_id=target_play.id).first()

        member.group_id = group.id
        db.session.commit()

        return member.to_dict()


    def get_groups_by_game(self, game_id):
        groups = Group.query.filter_by(game_id=game_id).all()
        result = []

        for group in groups:
            group_data = group.to_dict()
            members = Member.query.filter_by(group_id=group.id).all()
            group_data["members"] = [member.to_dict() for member in members]
            result.append(group_data)

        return result
