from flask import Blueprint, jsonify, request
from app.services.user import UserService


login_bp = Blueprint('login', __name__)
service = UserService()


@login_bp.route('/login', methods=['POST'])
def login():
	data = request.json or {}
	alias = data.get('alias')
	password = data.get('password')

	user = service.authenticate_user(alias, password)
	if not user:
		return jsonify({"error": "Invalid credentials"}), 401

	token = service.generate_token(user)
	return jsonify({
		"token": token,
		"user": user.to_dict()
	}), 200
