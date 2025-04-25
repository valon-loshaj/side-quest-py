"""
Run the Celery worker
"""

import os
import sys

# Set up Python path for imports - this needs to be BEFORE any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import and run the Celery worker
from src.side_quest_py.celery_app import celery_app

if __name__ == "__main__":
    argv = [
        "worker",
        "--loglevel=INFO",
    ]
    celery_app.worker_main(argv)
