# chat/routing.py
from django.urls import re_path, path

from .consumers import NotificationConsumer

websocket_urlpatterns = [
    #re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    path("notification_socket/", NotificationConsumer.as_asgi())
]