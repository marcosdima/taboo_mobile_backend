from flask import Flask
from app.extensions import db, migrate
from app.routes import main_bp
from app.models import User, Game, Plays # Migration.
import os


def create_app(test_config=None):
    app = Flask(__name__)

    db_uri = os.getenv('DATABASE_URL', 'sqlite:///app.db')

    # Fix Render postgres URL
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(main_bp)

    return app