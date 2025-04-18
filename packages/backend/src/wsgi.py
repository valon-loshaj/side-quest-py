"""WSGI Application Entry Point.

This module serves as the entry point for WSGI servers like Gunicorn.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Make sure FLASK_ENV is set
if not os.environ.get("FLASK_ENV"):
    os.environ["FLASK_ENV"] = "development"

from src.side_quest_py import create_app
from src.side_quest_py.config import config

env = os.environ.get("FLASK_ENV")
if not env:
    raise ValueError("FLASK_ENV is not set")

app = create_app()
app.config.from_object(config[env])

if __name__ == "__main__":
    app.run()
