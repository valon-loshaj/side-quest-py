"""WSGI Application Entry Point.

This module serves as the entry point for WSGI servers like Gunicorn.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.side_quest_py import create_app
from src.side_quest_py.config import config

# Get the environment from environment variable, default to development
env = os.environ.get("FLASK_ENV", "development")
app = create_app()
app.config.from_object(config[env])

if __name__ == "__main__":
    app.run()
