
from rest_framework.views import APIView
from findmychild.custom_methods import IsAuthenticatedCustom
from rest_framework.response import Response
from login_app.models import User
from rest_framework import generics, status
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from findmychild.custom_methods import IsAuthenticatedCustom
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class ChatRoomCreateView(generics.CreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def post(self, request, *args, **kwargs):
        data={}
        user = request.user
        other_user_id = request.data['otherUserId']
        other_user = get_object_or_404(User, id = other_user_id)
        try:
            chat_room = ChatRoom.objects.create()
            chat_room.users.add(user)
            chat_room.users.add(other_user)
            serialized_chat_room = self.serializer_class(chat_room).data
            return Response(serialized_chat_room, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class ChatRoomGetView(generics.RetrieveAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def get(self, request, *args, **kwargs):
        room_id = kwargs.get("id")
        try:
            chat_room_obj = ChatRoom.objects.get(id = room_id)
            data = self.serializer_class(chat_room_obj).data
        except Exception:
            raise Exception("Chat Room did not Found") 
        return Response(data, status=200)


class ChatRoomByUserView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = (IsAuthenticatedCustom, )  

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(users=user)
    
class MessageListByChatRoomView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_room_id = self.kwargs['id']
        return Message.objects.filter(chat_room_id=chat_room_id)

