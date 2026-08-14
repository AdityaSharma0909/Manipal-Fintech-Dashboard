"""
config/asgi.py
==============
ASGI entry point for async-capable servers (Uvicorn, Daphne).
Retained for future async support (WebSockets, SSE).
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_asgi_application()
