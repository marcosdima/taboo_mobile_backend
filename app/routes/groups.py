from flask import Blueprint, jsonify, request, g

from app.middlewares import token_required
from app.services import GroupsService, GameService


groups_bp = Blueprint('groups', __name__)
service = GroupsService()
game_service = GameService()


@groups_bp.route('/groups/assignments', methods=['POST'])
@token_required
def assign_user_to_group():
	data = request.json or {}
	user_id = data.get('user_id')
	group_id = data.get('group_id')

	if not user_id or not group_id:
		return jsonify({'error': 'user_id and group_id are required'}), 400

	group = service.get_group_by_id(group_id)
	if not group:
		return jsonify({'error': 'Group not found'}), 404

	requester_play = service.get_active_play_by_user_and_game(g.current_user.id, group['game_id'])
	if not requester_play:
		return jsonify({'error': 'Only players in this game can assign groups'}), 403

	target_play = service.get_active_play_by_user_and_game(user_id, group['game_id'])
	if not target_play:
		return jsonify({'error': 'User must be playing in this game'}), 400

	if service.get_member_by_play_id(target_play['id']):
		return jsonify({'error': 'User already assigned in this game. Use PUT to update'}), 400

	member = service.assign_user_to_group(
		requester_id=g.current_user.id,
		user_id=user_id,
		group_id=group_id,
	)
	return jsonify(member), 201


@groups_bp.route('/groups/assignments', methods=['PUT'])
@token_required
def reassign_user_group():
	data = request.json or {}
	user_id = data.get('user_id')
	group_id = data.get('group_id')

	if not user_id or not group_id:
		return jsonify({'error': 'user_id and group_id are required'}), 400

	group = service.get_group_by_id(group_id)
	if not group:
		return jsonify({'error': 'Group not found'}), 404

	game = game_service.get_game_by_id(group['game_id'])
	if not game or game['ended_at'] is not None:
		return jsonify({'error': 'Game does not exist or is not active'}), 400

	if g.current_user.id != game['creator']:
		return jsonify({'error': 'Only game creator can reassign groups'}), 403

	target_play = service.get_active_play_by_user_and_game(user_id, group['game_id'])
	if not target_play:
		return jsonify({'error': 'User must be playing in this game'}), 400

	if not service.get_member_by_play_id(target_play['id']):
		return jsonify({'error': 'User has no group assignment in this game'}), 404

	member = service.reassign_user_group(
		requester_id=g.current_user.id,
		user_id=user_id,
		group_id=group_id,
	)
	return jsonify(member), 200


@groups_bp.route('/groups/<int:game_id>', methods=['GET'])
@token_required
def get_groups_by_game(game_id):
	game = game_service.get_game_by_id(game_id)
	if not game:
		return jsonify({'error': 'Game not found'}), 404

	groups = service.get_groups_by_game(game_id)
	return jsonify(groups), 200
