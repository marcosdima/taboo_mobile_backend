from flask import Blueprint, request, jsonify, g
from app.services import GameService, PlaysService
from app.middlewares import token_required, creator_required


game_bp = Blueprint('game', __name__)
service = GameService()
plays_service = PlaysService()


@game_bp.route('/games', methods=['POST'])
@token_required
def create_game():
    creator_id = g.current_user.id

    if plays_service.is_playing(creator_id):
        return jsonify({"error": "Creator already has an active game"}), 400

    game = service.create_game({"creator": creator_id})
    return jsonify(game), 201


@game_bp.route('/games/<int:game_id>', methods=['PUT'])
@creator_required
def update_game(game_id):
    data = request.json
    game = service.update_game(game_id, data)
    return jsonify(game), 200


@game_bp.route('/games/<int:game_id>', methods=['DELETE'])
@creator_required
def delete_game(game_id):
    # TODO: Only allow deletion if game did not start yet.
    service.delete_game(game_id)
    return jsonify({"message": "Game deleted"}), 204


@game_bp.route('/games', methods=['GET'])
@token_required
def get_games():
    games = service.get_all()
    return jsonify(games), 200


@game_bp.route('/games/active', methods=['GET'])
@token_required
def get_active_games():
    games = service.get_active_games()
    return jsonify(games), 200


@game_bp.route('/games/start', methods=['POST'])
@token_required
def start_game():
    current_play = plays_service.get_current_play(g.current_user.id)

    if not current_play:
        return jsonify({"error": "User has no active game"}), 400

    game = service.get_game_by_id(current_play["game_id"])
    if not game or game["ended_at"] is not None:
        return jsonify({"error": "Game does not exist or is not active"}), 400

    if game["creator"] != g.current_user.id:
        return jsonify({"error": "Only game creator can start the game"}), 403

    players_in_game = len(plays_service.get_plays_by_game(game["id"]))
    if players_in_game < service.MIN_PLAYERS_TO_START:
        return jsonify({"error": f"Cannot start game with less than {service.MIN_PLAYERS_TO_START} players"}), 400

    started_game = service.start_game(game["id"])
    return jsonify(started_game), 200