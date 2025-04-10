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
    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Get environment, default to development if not specified
    env = os.environ.get("FLASK_ENV", "development")

    # Import config classes and apply environment-specific config
    from src.side_quest_py.config import config as config_dict  # noqa: E402

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
    from src.side_quest_py.routes.adventurer_routes import adventurer_bp  # noqa: E402
    from src.side_quest_py.routes.auth_routes import auth_bp  # noqa: E402
    from src.side_quest_py.routes.quest_routes import quest_bp  # noqa: E402
    from src.side_quest_py.routes.user_routes import user_bp  # noqa: E402

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
        from src.side_quest_py.db_utils import get_db_status  # noqa: E402

        status = get_db_status()
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

    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables without dropping existing data."""
        print("Initializing the database...")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        from src.side_quest_py.db_utils import init_db  # noqa: E402

        init_db(app)
        print("Database initialized successfully")

    @app.cli.command("reset-db")
    def reset_db_command():
        """Clear existing data and create new tables."""
        print("Resetting the database...")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        from src.side_quest_py.db_utils import reset_db  # noqa: E402

        reset_db(app)
        print("Database reset successfully")

    @app.cli.command("seed-db")
    def seed_db_command():
        """Seed the database with sample data."""
        print("Seeding the database...")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        try:
            from src.side_quest_py.db_utils import seed_db  # noqa: E402

            seed_db(app)
            print("Database seeded successfully")
        except Exception as e:
            print(f"Error seeding database: {e}")
            raise

    @app.cli.command("db-status")
    def db_status_command():
        """Show database connection status."""
        from src.side_quest_py.db_utils import get_db_status  # noqa: E402

        status = get_db_status(app)

        print(f"Database status: {status['status']}")
        print(f"Database URI: {status['uri']}")
        print(f"Environment: {status['env']}")

        return status


# Create a default application instance for Flask CLI commands
default_app = create_app()
