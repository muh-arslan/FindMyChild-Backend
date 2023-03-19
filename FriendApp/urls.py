from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import ListAllFriendsView, SendFriendRequestView, ListAllFriendRequestView, AcceptRequestView, DeleteRequestView, UnfriendView, PeopleYouMayKnow

urlpatterns = [
            path('FriendApp/api/friends/list', ListAllFriendsView.as_view(), name="friend_list_view"),
            path('FriendApp/api/friend-request/send', SendFriendRequestView.as_view(), name="send_friend_request_view"),
            path('FriendApp/api/list-friend-requests', ListAllFriendRequestView.as_view(), name="list_friend_requests_view"),
            path('FriendApp/api/accept-friend-request', AcceptRequestView.as_view(), name="accept_request_view"),
            path('FriendApp/api/delete-friend-request/<int:id>', DeleteRequestView.as_view(), name="delete_request_view"),
            path('FriendApp/api/friends/<int:user_id>/unfriend', UnfriendView.as_view(), name="unfriend_view"),
            path('FriendApp/api/friends/people-you-may-know', PeopleYouMayKnow.as_view(), name="people_you_may_know_view"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)