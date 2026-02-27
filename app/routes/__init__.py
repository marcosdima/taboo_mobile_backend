from flask import Blueprint
from .games import game_bp


main_bp = Blueprint('main', __name__)
main_bp.register_blueprint(game_bp)