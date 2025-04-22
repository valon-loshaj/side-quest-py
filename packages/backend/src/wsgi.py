"""WSGI Application Entry Point.

This module serves as the entry point for WSGI servers like Gunicorn.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Make sure FASTAPI_ENV is set
if not os.environ.get("FASTAPI_ENV"):
    os.environ["FASTAPI_ENV"] = "development"

from src.side_quest_py import create_app

env = os.environ.get("FASTAPI_ENV")
if not env:
    raise ValueError("FASTAPI_ENV is not set")

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("wsgi:app", host="0.0.0.0", port=8000, reload=True)
