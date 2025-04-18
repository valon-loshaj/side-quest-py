"""Side Quest Py - A Flask-based adventure game backend.

This module serves as the main entry point for the Side Quest Py application.
It initializes the Flask application, configures extensions, and sets up routes.
"""

import os
from typing import Optional, Union

from flask import Flask, current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.side_quest_py.config import config as config_dict, Config

INSTANCE_PATH = Config.INSTANCE_PATH

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
    # Get environment, throw an error if it's not set
    env = os.environ.get("FLASK_ENV")
    if not env:
        raise ValueError("FLASK_ENV is not set")

    # Ensure the instance directory exists
    os.makedirs(INSTANCE_PATH, exist_ok=True)

    # Create Flask app with custom instance path
    app = Flask(__name__, instance_path=INSTANCE_PATH)

    # Apply configuration
    app.config.from_object(config_dict[env])

    # Override with any passed config values
    if config:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register CLI commands
    register_cli_commands(app)

    # Import blueprints
    from src.side_quest_py.routes.adventurer_routes import adventurer_bp
    from src.side_quest_py.routes.auth_routes import auth_bp
    from src.side_quest_py.routes.quest_routes import quest_bp
    from src.side_quest_py.routes.user_routes import user_bp

    # Register blueprints
    app.register_blueprint(adventurer_bp, url_prefix="/api/v1")
    app.register_blueprint(quest_bp, url_prefix="/api/v1")
    app.register_blueprint(user_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

    # Add a simple route to verify the app is working
    @app.route("/hello")
    def hello():
        return "Hello, Side Quest!"

    # Add health check endpoint
    @app.route("/health")
    def health_check():
        from scripts.db.db_utils import get_db_status

        status = get_db_status(current_app)
        return {
            "status": "healthy" if status["status"] == "connected" else "unhealthy",
            "db": status,
            "app": {"env": app.config.get("ENV", env), "debug": app.debug},
        }

    return app


def register_cli_commands(app: Flask) -> None:
    """Register CLI commands with the Flask application.

    Args:
        app: Flask application instance
    """
    # Import the CLI command functions from the scripts
    from scripts.db.init_db import init_db_command as init_db
    from scripts.db.reset_db import reset_db_command as reset_db
    from scripts.db.seed_db import seed_db_command as seed_db

    # Register the commands with the application
    app.cli.add_command(init_db)
    app.cli.add_command(reset_db)
    app.cli.add_command(seed_db)

    @app.cli.command("db-status")
    def db_status_command():
        """Show database connection status."""
        from scripts.db.db_utils import get_db_status

        status = get_db_status(app)

        print(f"Database status: {status['status']}")
        print(f"Database URI: {status['uri']}")
        print(f"Environment: {status['env']}")

        return status


# Create a default application instance for Flask CLI commands
default_app = create_app()
