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


@login_bp.route('/validate', methods=['POST'])
def validate_token():
	auth_header = request.headers.get("Authorization", "")

	token = ""
	if auth_header.startswith("Bearer "):
		token = auth_header.split(" ", 1)[1].strip()

	if not token:
		return jsonify({"error": "Token is missing or invalid"}), 401

	validation = service.validate_token(token)
	status = validation.get("status", "invalid")

	if status == "valid":
		user = validation.get("user")
		return jsonify({
			"token": token,
			"user": user.to_dict()
		}), 200

	if status == "expired":
		return jsonify({"error": "Token has expired"}), 401

	return jsonify({"error": "Token is missing or invalid"}), 401
