# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    #path("", views.index, name="index"),
    #path("<str:room_name>/", views.ChatRoomView.as_view(), name="room"),
    path("chat-room_create/", views.ChatRoomCreateView.as_view(), name="create_room"),
    path("chat-room/<uuid:id>", views.MessageListByChatRoomView.as_view(), name="messages"),
    path("", views.ChatRoomByUserView.as_view(), name="get_user_room"),
    
]