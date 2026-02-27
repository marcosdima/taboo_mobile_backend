from flask import Blueprint, request, jsonify
from app.services import GameService, UserService



game_bp = Blueprint('game', __name__)
service = GameService()


@game_bp.route('/games', methods=['POST'])
def create_game():
    data = request.json

    creator_id = data.get("creator")
    if not creator_id:
        return jsonify({"error": "Creator ID is required"}), 400
    
    user_service = UserService()
    if not user_service.user_exists(creator_id):
        return jsonify({"error": "Creator does not exist"}), 400
    
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


@game_bp.route('/games', methods=['GET'])
def get_games():
    games = service.get_all()
    return jsonify(games), 200