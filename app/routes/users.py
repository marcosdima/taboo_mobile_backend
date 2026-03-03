from flask import Blueprint, request, jsonify
from app.services.user import UserService
from app.middlewares import token_required


users_bp = Blueprint('users', __name__)
service = UserService()



@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json

    try:
        user = service.create_user(data)
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    user = service.get_user(user_id)
    return jsonify(user), 200


@users_bp.route('/users', methods=['GET'])
@token_required
def get_all_users():
    users = service.get_all_users()
    return jsonify(users), 200


@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    data = request.json
    user = service.update_user(user_id, data)
    return jsonify(user), 200


@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    service.delete_user(user_id)
    return jsonify({"message": "User deleted"}), 204