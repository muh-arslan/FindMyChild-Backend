from rest_framework import generics, status, views
from channels.layers import get_channel_layer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from channels.db import database_sync_to_async
from .consumers import NotificationConsumer
from .models import MatchNotification, DropChildNotification
from login_app.models import User
from .serializers import MatchNotificationSerializer, DropChildNotificationSerializer, ContactUsSerializer, FeedbackReviewSerializer
from findmychild.custom_methods import IsAuthenticatedCustom
from django.shortcuts import get_object_or_404

# class NotificationCreateView(generics.CreateAPIView):
#     queryset = Notification.objects.all()
#     serializer_class = NotificationSerializer
#     permission_classes = (IsAuthenticatedCustom, )

#     def post(self, request, *args, **kwargs):
#         data={}
#         user = request.user
#         other_user_id = request.data['otherUserId']
#         other_user = User.objects.get(id = other_user_id)
#         if user.user_type == 'appUser':
#             appUser = user
#             orgUser = other_user
#         else:
#             appUser = other_user
#             orgUser = user

#         data["room_name"] = f"chat_{min(user.first_name, other_user.first_name)}_{max(user.first_name, other_user.first_name)}"
#         serializer = self.serializer_class(data = data)
#         if serializer.is_valid():
#             serializer.save(appUser = appUser, orgUser = orgUser)
#             print(serializer.errors)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ListUserNotificationsView(generics.ListAPIView):
#     serializer_class = MatchNotificationSerializer
#     permission_classes = (IsAuthenticatedCustom, )

#     def list(self, request, *args, **kwargs):
#         user = request.user
#         matchNotifications = MatchNotification.objects.filter(user_id = user.id)

#         serializedNotifications = MatchNotificationSerializer(matchNotifications, many=True).data

#         return Response(serializedNotifications)


class ListUserNotificationsView(generics.ListAPIView):
    permission_classes = (IsAuthenticatedCustom,)
    serializer_class = {
        'match_notifications': MatchNotificationSerializer,
        'drop_chid_notifications': DropChildNotificationSerializer
    }

    def get_queryset(self):
        user = self.request.user
        queryset = {
            "match_notifications": MatchNotification.objects.filter(user_id=user.id),
            "drop_chid_notifications": DropChildNotification.objects.filter(user_id=user.id),
        }
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serialized_data = {}
        for key in queryset:
            serializer = self.serializer_class[key](queryset[key], many=True)
            serialized_data[key] = serializer.data
        return Response(serialized_data)


class ContactUsView(views.APIView):
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedbackReviewView(views.APIView):
    def post(self, request):
        serializer = FeedbackReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
