from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate
from app.routes import main_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register the main blueprint.
    app.register_blueprint(main_bp)

    return app
