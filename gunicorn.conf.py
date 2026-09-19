"""Gunicorn production defaults for Nele."""

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1
worker_class = "gthread"
threads = 4
timeout = 120
keepalive = 5
preload_app = False
