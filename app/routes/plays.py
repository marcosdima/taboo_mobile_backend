from flask import Blueprint, request, jsonify
from app.services import PlaysService

plays_bp = Blueprint('plays', __name__)
service = PlaysService()


@plays_bp.route('/plays', methods=['POST'])
def add_play():
    """Add a user to a game (create a play record)"""
    data = request.json

    try:
        play = service.add_play(data)
        return jsonify(play), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@plays_bp.route('/plays/<int:user_id>/<int:game_id>', methods=['DELETE'])
def delete_play(user_id, game_id):
    """Remove a user from a game"""
    success = service.delete_play(user_id, game_id)
    if success:
        return jsonify({"message": "Play deleted"}), 204
    return jsonify({"error": "Play not found"}), 404


@plays_bp.route('/plays/game/<int:game_id>', methods=['GET'])
def get_plays_by_game(game_id):
    """Get all plays in a game"""
    plays = service.get_plays_by_game(game_id)
    return jsonify(plays), 200


@plays_bp.route('/plays/user/<int:user_id>', methods=['GET'])
def get_plays_by_user(user_id):
    """Get all games where a user plays"""
    plays = service.get_plays_by_user(user_id)
    return jsonify(plays), 200


@plays_bp.route('/plays', methods=['GET'])
def get_all_plays():
    """Get all plays"""
    plays = service.get_all_plays()
    return jsonify(plays), 200
