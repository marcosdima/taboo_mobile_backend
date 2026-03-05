from flask import Blueprint, jsonify, request, g

from app.middlewares import token_required
from app.services import GroupsService


groups_bp = Blueprint('groups', __name__)
service = GroupsService()


@groups_bp.route('/groups/assignments', methods=['POST'])
@token_required
def assign_user_to_group():
	data = request.json or {}

	try:
		member = service.assign_user_to_group(
			requester_id=g.current_user.id,
			user_id=data.get('user_id'),
			group_id=data.get('group_id'),
		)
		return jsonify(member), 201
	except LookupError as e:
		return jsonify({'error': str(e)}), 404
	except PermissionError as e:
		return jsonify({'error': str(e)}), 403
	except ValueError as e:
		return jsonify({'error': str(e)}), 400


@groups_bp.route('/groups/assignments', methods=['PUT'])
@token_required
def reassign_user_group():
	data = request.json or {}

	try:
		member = service.reassign_user_group(
			requester_id=g.current_user.id,
			user_id=data.get('user_id'),
			group_id=data.get('group_id'),
		)
		return jsonify(member), 200
	except LookupError as e:
		return jsonify({'error': str(e)}), 404
	except PermissionError as e:
		return jsonify({'error': str(e)}), 403
	except ValueError as e:
		return jsonify({'error': str(e)}), 400


@groups_bp.route('/groups/<int:game_id>', methods=['GET'])
@token_required
def get_groups_by_game(game_id):
	try:
		groups = service.get_groups_by_game(game_id)
		return jsonify(groups), 200
	except LookupError as e:
		return jsonify({'error': str(e)}), 404
