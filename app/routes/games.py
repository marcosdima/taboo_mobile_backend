from flask import Blueprint, request, jsonify
from app.services.game import GameService


game_bp = Blueprint('game', __name__)
service = GameService()


@game_bp.route('/games', methods=['POST'])
def create_game():
    data = request.json
    game = service.create_game(data)
    return jsonify(game), 201


@game_bp.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    data = request.json
    game = service.update_game(game_id, data)
    return jsonify(game), 200


@game_bp.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    service.delete_game(game_id)
    return jsonify({"message": "Game deleted"}), 204