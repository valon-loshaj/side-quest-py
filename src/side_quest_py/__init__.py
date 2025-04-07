from typing import Optional, Union

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .routes.adventurer_routes import adventurer_bp
from .routes.quest_routes import quest_bp
from .routes.user_routes import user_bp

# Initialize SQLAlchemy instance at module level
db = SQLAlchemy()
migrate = Migrate()


def create_app(config: Optional[Union[dict, object]] = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config (Optional[Union[dict, object]]): Configuration dictionary or object to override defaults

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Configure the app with default settings
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///side_quest.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("SECRET_KEY", "dev")  # Change this in production

    # Override with any passed config values
    if config:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(adventurer_bp, url_prefix="/api/v1")
    app.register_blueprint(quest_bp, url_prefix="/api/v1")
    app.register_blueprint(user_bp, url_prefix="/api/v1")

    return app
