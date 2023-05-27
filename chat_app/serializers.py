from rest_framework import serializers
from .models import GenericFileUpload, Message, MessageAttachment, ChatRoom
from login_app.serializers import UserSerializer

class GenericFileUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = GenericFileUpload
        fields = "__all__"


class MessageAttachmentSerializer(serializers.ModelSerializer):
    attachment = GenericFileUploadSerializer()

    class Meta:
        model = MessageAttachment
        fields = "__all__"

class ChatRoomSerializer(serializers.ModelSerializer):

    users = UserSerializer(many=True)
    
    class Meta:
        model = ChatRoom
        fields = "__all__"        

class MessageSerializer(serializers.ModelSerializer):
    # sender = UserSerializer(read_only=True)
    # reciever = UserSerializer(read_only=True)
    sender = serializers.SerializerMethodField()
    reciever = serializers.SerializerMethodField()
    chat_room = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = "__all__"
    
    def get_sender(self, obj):
        return {"id": str(obj.sender.id), "first_name": obj.sender.first_name}

    def get_reciever(self, obj):
        return {"id": str(obj.reciever.id), "first_name": obj.reciever.first_name}
    
    def get_chat_room(self, obj):
        return str(obj.chat_room.id)
"""
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reciever = UserSerializer(read_only=True)
    chat_room = ChatRoomSerializer(read_only=True)
    

    class Meta:
        model = Message
        fields = "__all__"
    

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    reciever = serializers.SerializerMethodField()
    chat_room = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "chat_room",
            "sender",
            "reciever",
            "message",
        )

    def get_chat_room(self, obj):
        return str(obj.chat_room.id)

    def get_sender(self, obj):
        return UserSerializer(obj.sender).data

    def get_reciever(self, obj):
        return UserSerializer(obj.reciever).data
    
"""

