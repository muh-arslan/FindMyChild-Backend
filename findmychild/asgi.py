"""
ASGI config for findmychild project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from chat_app.middleware import TokenAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "findmychild.settings")

django_asgi_app = get_asgi_application()

import chat_app.routing
import notification_app.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddleware(URLRouter(
                chat_app.routing.websocket_urlpatterns+
                notification_app.routing.websocket_urlpatterns))
        )
    }
)