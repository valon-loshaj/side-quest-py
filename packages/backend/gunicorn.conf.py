"""
Gunicorn configuration file for the backend.
"""

from multiprocessing import cpu_count
from src.side_quest_py.api.config import get_settings

# Server socket
bind = get_settings().GUNICORN_BIND

# Worker processes
workers = cpu_count()
worker_class = get_settings().GUNICORN_WORKER_CLASS

# Environment settings
raw_env = [
    f"FASTAPI_ENV={get_settings().FASTAPI_ENV}",
]

# Reload in development
reload = get_settings().FASTAPI_ENV != "production"

# Set unlimited request line and header field size
limit_request_line = 0
limit_request_fields = 0

# Logging
accesslog = get_settings().GUNICORN_ACCESS_LOG
errorlog = get_settings().GUNICORN_ERROR_LOG
loglevel = get_settings().GUNICORN_LOG_LEVEL

# Timeout settings
timeout = get_settings().GUNICORN_TIMEOUT
keepalive = get_settings().GUNICORN_KEEPALIVE
