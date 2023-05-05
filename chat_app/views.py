
from rest_framework.views import APIView
from findmychild.custom_methods import IsAuthenticatedCustom
from rest_framework.response import Response
from login_app.models import User
from rest_framework import generics, status
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, ChatRoomsByUserSerializer
from findmychild.custom_methods import IsAuthenticatedCustom
from django.shortcuts import get_object_or_404

class ChatRoomCreateView(generics.CreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
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


class ChatRoomGetView(generics.RetrieveAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def get(self, request, *args, **kwargs):
        room_id = kwargs.get("id")
        chat_room_obj = ChatRoom.objects.get(id = room_id)
        data = {}
        try:
            data = self.serializer_class(chat_room_obj).data
        except Exception:
            raise Exception("Chat Room did not Found") 
        return Response(data, status=200)


class ChatRoomByUserView(APIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomsByUserSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def post(self, request):

        user_id = request.data.get('user_id', None)
        #print(user_id)
        if user_id is None:
            return Response({'error': 'user_id not provided'}, status=400)
        
        user = get_object_or_404(User, id=user_id)
        if user.user_type == "appUser":
            chat_rooms = ChatRoom.objects.filter(appUser=user)
        else:
            chat_rooms = ChatRoom.objects.filter(orgUser=user)
        serializer = self.serializer_class(chat_rooms, many=True)
        return Response(serializer.data)

