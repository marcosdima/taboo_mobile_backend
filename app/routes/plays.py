from flask import Blueprint, request, jsonify, g
from app.services import PlaysService, GameService
from app.middlewares import token_required

plays_bp = Blueprint('plays', __name__)
service = PlaysService()
game_service = GameService()


@plays_bp.route('/play', methods=['POST'])
@token_required
def add_play():
    """Add a user to a game (create a play record)"""
    data = request.json or {}
    game_id = data.get("game_id")

    if not game_id:
        return jsonify({"error": "User ID and Game ID are required"}), 400

    game = game_service.get_game_by_id(game_id)
    if not game or game["ended_at"] is not None:
        return jsonify({"error": "Game does not exist or is not active"}), 400

    if service.get_play(g.current_user.id, game_id):
        return jsonify({"error": "User already playing in this game"}), 400

    if service.count_plays_by_game(game_id) >= game_service.MAX_PLAYS_PER_GAME:
        return jsonify({"error": f"Game already has maximum of {game_service.MAX_PLAYS_PER_GAME} plays"}), 400

    play = service.add_play({
        "user_id": g.current_user.id,
        "game_id": game_id
    })
    return jsonify(play), 201


@plays_bp.route('/leave', methods=['DELETE'])
@token_required
def delete_play():
    """Remove a user from a game"""
    deleted = service.delete_current_plays(g.current_user.id)
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


@plays_bp.route('/plays/user', methods=['GET'])
@token_required
def get_plays_by_user():
    """Get current active play for authenticated user"""
    plays = service.get_current_play(g.current_user.id)
    if not plays:
        return jsonify({"error": "No active play found for user"}), 404
    return jsonify(plays), 200


@plays_bp.route('/plays', methods=['GET'])
@token_required
def get_all_plays():
    """Get all plays"""
    plays = service.get_all_plays()
    return jsonify(plays), 200
