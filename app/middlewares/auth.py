from functools import wraps
from flask import request, jsonify, g
from app.services.user import UserService


service = UserService()


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        user = service.get_user_from_token(token)

        if not user:
            return jsonify({"error": "Token is missing or invalid"}), 401

        g.current_user = user
        return func(*args, **kwargs)

    return decorated
