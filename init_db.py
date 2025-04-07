import os

from dotenv import load_dotenv
from flask_migrate import upgrade

from src.side_quest_py import create_app, db
from src.side_quest_py.config import config

# Import the SQLAlchemy models
from src.side_quest_py.models.db_models import Adventurer, Quest

# Load environment variables from .env file
load_dotenv()

# Get the environment from environment variable, default to development
env = os.environ.get("FLASK_ENV", "development")
print(f"Current environment: {env}")

# Create app with proper configuration
app = create_app()
app.config.from_object(config[env])

# Print configuration for debugging
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"App instance path: {app.instance_path}")
print(f"Current working directory: {os.getcwd()}")

# Apply migrations instead of creating tables directly
with app.app_context():
    # Apply migrations
    upgrade()
    print(f"Migrations applied to: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # List all tables created
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables available: {tables}")

    # Add some sample data if tables are empty
    if tables and not Adventurer.query.first():
        # Create a sample adventurer
        sample_adventurer = Adventurer(name="Sample Adventurer", level=1, experience=0)
        db.session.add(sample_adventurer)

        # Create a sample quest
        sample_quest = Quest(
            id="sample-quest-001", title="Sample Quest", experience_reward=100
        )
        db.session.add(sample_quest)

        db.session.commit()
        print("Sample data added to the database!")
