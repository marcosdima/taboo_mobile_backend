from flask import Blueprint, request, jsonify
from app.services import PlaysService
from app.middlewares import token_required

plays_bp = Blueprint('plays', __name__)
service = PlaysService()


@plays_bp.route('/play', methods=['POST'])
@token_required
def add_play():
    """Add a user to a game (create a play record)"""
    data = request.json

    try:
        play = service.add_play(data)
        return jsonify(play), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@plays_bp.route('/leave', methods=['DELETE'])
@token_required
def delete_play():
    """Remove a user from a game"""
    data = request.json
    user_id = data.get("user_id")
    
    deleted = service.delete_current_plays(user_id)
    if deleted:
        return jsonify({"message": "Play removed"}), 204
    else:
        return jsonify({"error": "Play not found"}), 404


@plays_bp.route('/plays/game/<int:game_id>', methods=['GET'])
@token_required
def get_plays_by_game(game_id):
    """Get all plays in a game"""
    plays = service.get_plays_by_game(game_id)
    return jsonify(plays), 200


@plays_bp.route('/plays/user/<int:user_id>', methods=['GET'])
@token_required
def get_plays_by_user(user_id):
    """Get all games where a user plays"""
    plays = service.get_current_play(user_id)
    if not plays:
        return jsonify({"error": "No active play found for user"}), 404
    return jsonify(plays), 200


@plays_bp.route('/plays', methods=['GET'])
@token_required
def get_all_plays():
    """Get all plays"""
    plays = service.get_all_plays()
    return jsonify(plays), 200
