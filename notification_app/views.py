# from django.shortcuts import render
# from rest_framework.viewsets import ModelViewSet
# from rest_framework.views import APIView
# from .serializers import GenericFileUpload, GenericFileUploadSerializer, Message, MessageAttachment, MessageSerializer
# from findmychild.custom_methods import IsAuthenticatedCustom
# from rest_framework.response import Response
# from django.db.models import Q
# from login_app.models import User
# from django.conf import settings
# import requests
# import json



# def index(request):
#     return render(request, "chat_template/index.html")

# def room(request, room_name):
#     return render(request, "chat_template/room.html", {"room_name": room_name})

# """
# def handleRequest(serializerData):
#     notification = {
#         "message": serializerData.data.get("message"),
#         "from": serializerData.data.get("sender"),
#         "receiver": serializerData.data.get("receiver").get("id")
#     }

#     headers = {
#         'Content-Type': 'application/json',
#     }
#     try:
#         requests.post(settings.SOCKET_SERVER, json.dumps(
#             notification), headers=headers)
#     except Exception as e:
#         pass
#     return True


# class GenericFileUploadView(ModelViewSet):
#     queryset = GenericFileUpload.objects.all()
#     serializer_class = GenericFileUploadSerializer


# class MessageView(ModelViewSet):
#     queryset = Message.objects.select_related(
#         "sender", "receiver").prefetch_related("message_attachments")
#     serializer_class = MessageSerializer
#     permission_classes = (IsAuthenticatedCustom, )

#     def get_queryset(self):
#         data = self.request.query_params.dict()
#         user_id = data.get("user_id", None)

#         if user_id:
#             active_user_id = self.request.user.id
#             return self.queryset.filter(Q(sender_id=user_id, receiver_id=active_user_id) | Q(
#                 sender_id=active_user_id, receiver_id=user_id)).distinct()
#         return self.queryset

#     def create(self, request, *args, **kwargs):

#         try:
#             request.data._mutable = True
#         except:
#             pass
#         attachments = request.data.pop("attachments", None)

#         if str(request.user.id) != str(request.data.get("sender_id", None)):
#             raise Exception("only sender can create a message")

#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         if attachments:
#             MessageAttachment.objects.bulk_create([MessageAttachment(
#                 **attachment, message_id=serializer.data["id"]) for attachment in attachments])

#             message_data = self.get_queryset().get(id=serializer.data["id"])
#             return Response(self.serializer_class(message_data).data, status=201)

#         handleRequest(serializer)

#         return Response(serializer.data, status=201)

#     def update(self, request, *args, **kwargs):

#         try:
#             request.data._mutable = True
#         except:
#             pass
#         attachments = request.data.pop("attachments", None)
#         instance = self.get_object()

#         serializer = self.serializer_class(
#             data=request.data, instance=instance, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         MessageAttachment.objects.filter(message_id=instance.id).delete()

#         if attachments:
#             MessageAttachment.objects.bulk_create([MessageAttachment(
#                 **attachment, message_id=instance.id) for attachment in attachments])

#             message_data = self.get_object()
#             return Response(self.serializer_class(message_data).data, status=200)

#         handleRequest(serializer)

#         return Response(serializer.data, status=200)


# class ReadMultipleMessages(APIView):

#     def post(self, request):
#         data = request.data.get("message_ids", None)

#         Message.objects.filter(id__in=data).update(is_read=True)
#         return Response("success")
    
# """
# """
# New Code
# """
from rest_framework import generics, status
from channels.layers import get_channel_layer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from channels.db import database_sync_to_async
from .consumers import NotificationConsumer
from .models import Notification
from login_app.models import User
from .serializers import NotificationSerializer
from findmychild.custom_methods import IsAuthenticatedCustom
import uuid
from django.shortcuts import get_object_or_404

class ChatRoomCreateView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def post(self, request, *args, **kwargs):
        data={}
        user = request.user
        other_user_id = request.data['otherUserId']
        other_user = User.objects.get(id = other_user_id)
        if user.user_type == 'appUser':
            appUser = user
            orgUser = other_user
        else:
            appUser = other_user
            orgUser = user
        
        data["room_name"] = f"chat_{min(user.first_name, other_user.first_name)}_{max(user.first_name, other_user.first_name)}"
        serializer = self.serializer_class(data = data)
        if serializer.is_valid():
            serializer.save(appUser = appUser, orgUser = orgUser)
            print(serializer.errors)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


