from django.shortcuts import render
from .models import FriendList, FriendRequest
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView, ListCreateAPIView, DestroyAPIView
from .serializers import FriendListSerializer, RequestSerializer, FriendRequestSerializer
from rest_framework.response import Response
from LoginApp.models import User
from LoginApp.serializers import UserSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from chatApp.models import ChatThread
from itertools import chain
# Create your views here.

class ListAllFriendsView(ListAPIView):
    queryset = FriendList.objects.all()
    serializer_class = FriendListSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        obj = FriendList.objects.filter(user=request.user)
        friend_list_serializer = self.serializer_class(obj, many=True, context={"request":request})
            # when we user 'filter' while querying data we need to return friend_list_serializer.data so data is in json
        return Response(friend_list_serializer.data)
        
class SendFriendRequestView(CreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            receiver = User.objects.get(id=request.data["id"])
            send_request = FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
            return Response({"message":"Friend Request Sent"})
        except Exception as e:
            return Response(e)

class ListAllFriendRequestView(ListAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    def get(self,request):
        obj = FriendRequest.objects.filter(receiver=request.user)  
        print(request.user)
        friend_request_list_serializer = self.serializer_class(obj, many=True, context={"request":request})
            # when we user 'filter' while querying data we need to return friend_list_serializer.data so data is in json
        return Response(friend_request_list_serializer.data)
        
class AcceptRequestView(APIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            friend_request = FriendRequest.objects.get(id=request.data["id"])
            my_friend_list = FriendList.objects.get_or_create(user=request.user)
            print(my_friend_list[0].user)
            my_friend_list[0].friends.add(friend_request.sender)
            sender_friend_list = FriendList.objects.get_or_create(user=friend_request.sender)
            sender_friend_list[0].friends.add(request.user)
            friend_request.delete()
            chat_thread = ChatThread.objects.get_or_create(sender=request.user, receiver=friend_request.sender)
            return Response({"message": "Friend Request Accepted"})
        except Exception as e:
            return Response({":message":"Something went wrong"})
        
class DeleteRequestView(DestroyAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = FriendRequest.objects.all()
    lookup_field = 'id'
    
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response({"status":"Particular Request has been deleted"})
    
class UnfriendView(APIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        try:
            my_friend_list = FriendList.objects.get_or_create(user=request.user)
            user_to_remove = User.objects.get(id=user_id)
            my_friend_list[0].friends.remove(user_to_remove)
            removee_friend_list = FriendList.objects.get_or_create(user=user_to_remove)
            removee_friend_list[0].friends.remove(request.user)
            return Response({"message": "Unfriended Successfully"})
        except Exception as e:
            return Response({":message":"Something went wrong"})
        
class PeopleYouMayKnow(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # here i am getting all the friends' ids of logged in user
        all_friends_ids = FriendList.objects.filter(user=request.user).values_list("friends", flat=True)
        # here i am excluding all users whose ids are same as of 'all_friends_ids' and the logged in user from all users
        all_stranger_user = User.objects.all().exclude(id__in=all_friends_ids).exclude(id__in=[request.user.id])
        user_serializer = self.serializer_class(all_stranger_user, many=True, context={"request":request})
        if user_serializer:
            # when we user 'filter' while querying data we need to return friend_list_serializer.data so data is in json
            return Response(user_serializer.data)
        else:
            return Response({"message":"something went wrong"})
        

        
        
