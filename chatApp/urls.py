from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import ListAllThreadOfLoggedUser, ListAllMessagesInThread, SendMessageInChatThread
from django.conf.urls.static import static

urlpatterns = [
        path('chatApp/api/chats/list', ListAllThreadOfLoggedUser.as_view(), name="list_all_threads"),
        path('chatApp/api/messages/<int:chat_id>/list', ListAllMessagesInThread.as_view(), name="list_all_messages_in_thread"),
        path('chatApp/api/messages/send', SendMessageInChatThread.as_view(), name="send_message_in_thread"),
        
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)