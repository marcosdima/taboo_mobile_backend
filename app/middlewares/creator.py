from functools import wraps
from flask import request, jsonify, g

from app.extensions import db
from app.models import Game
from app.services.user import UserService


service = UserService()


def creator_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        # Authenticate user from Bearer token.
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing or invalid"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        user = service.get_user_from_token(token)

        if not user:
            return jsonify({"error": "Token is missing or invalid"}), 401

        # Resolve game_id from route params first, then body as fallback.
        game_id = kwargs.get("game_id")
        if game_id is None:
            payload = request.get_json(silent=True) or {}
            game_id = payload.get("game_id")

        if game_id is None:
            return jsonify({"error": "game_id is required"}), 400

        game = db.session.get(Game, game_id)
        if game is None:
            return jsonify({"error": "Game not found"}), 404

        # Authorize only the game creator.
        if game.creator != user.id:
            return jsonify({"error": "Only game creator can perform this action"}), 403

        g.current_user = user
        g.current_game = game
        return func(*args, **kwargs)

    return decorated
