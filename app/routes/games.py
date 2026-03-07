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