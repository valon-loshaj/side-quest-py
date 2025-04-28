"""
Run the Celery beat scheduler
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import and run the Celery beat scheduler
from src.side_quest_py.celery_app import celery_app

if __name__ == "__main__":
    argv = [
        "beat",
        "--loglevel=INFO",
    ]
    celery_app.worker_main(argv)
