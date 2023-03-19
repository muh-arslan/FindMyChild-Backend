from django.shortcuts import render
from .models import Message, ChatThread, photos
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView, ListCreateAPIView
from .serializers import MessageSerializer, ChatThreadSerializer
from rest_framework.response import Response
from LoginApp.models import User
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.renderers import JSONRenderer, MultiPartRenderer

# Create your views here.

class ListAllThreadOfLoggedUser(ListAPIView):
    queryset = ChatThread.objects.all()
    serializer_class = ChatThreadSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # if you want to execute 'OR' in django query that is how
        thread = ChatThread.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        thread_serialized = self.serializer_class(thread, many=True, context={"request":request})
        return Response(thread_serialized.data)
    
class ListAllMessagesInThread(ListAPIView):
    queryset = ChatThread.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, chat_id):
        try:
            thread = ChatThread.objects.get(id=chat_id)
            if thread.sender == request.user or thread.receiver == request.user:
                messages = Message.objects.filter(thread=thread)
                messages_serialized = self.serializer_class(messages, many=True, context={"request":request})
                return Response(messages_serialized.data)
            else:
                return Response({"message":"you can not see messages of someone else's chat"})
        except Exception as e:
            print(e)
            return Response({"message":"No chat present of specified id"})
        
class SendMessageInChatThread(ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    # renderer_classes = [MultiPartRenderer]
    def post(self, request):
        response = dict()
        message_serialized = self.serializer_class(data=request.data, context={'request': request})
        # print("these are files", request.data)
        if message_serialized.is_valid():
            message_serialized.save()
            return Response({"status": "Your message has been sent"})
        else:
            print(message_serialized.errors)
            return Response({"status": "Your message could not be sent been sent"})