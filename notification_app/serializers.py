from rest_framework import serializers
from .models import MatchNotification
from login_app.serializers import UserSerializer
from lostchildren.serializers import MatchingChildSerializer, LostChildSerializer

class MatchNotificationSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    matching_child = MatchingChildSerializer(read_only=True)
    lost_child = LostChildSerializer(read_only=True)
    
    class Meta:
        model = MatchNotification
        fields = "__all__"

# class ChatRoomsByUserSerializer(serializers.ModelSerializer):

#     appUser = serializers.SerializerMethodField()
#     orgUser = serializers.SerializerMethodField()

#     class Meta:
#         model = ChatRoom
#         fields = ["id", "appUser", "orgUser"]

#     def get_appUser(self, obj):
#         return {"id": obj.appUser.id, "first_name": obj.appUser.first_name}

#     def get_orgUser(self, obj):
#         return {"id": obj.orgUser.id, "first_name": obj.orgUser.first_name}
        

# class MessageSerializer(serializers.ModelSerializer):
#     # sender = UserSerializer(read_only=True)
#     # reciever = UserSerializer(read_only=True)
#     sender = serializers.SerializerMethodField()
#     reciever = serializers.SerializerMethodField()
#     chat_room = serializers.SerializerMethodField()

#     class Meta:
#         model = Message
#         fields = "__all__"
    
#     def get_sender(self, obj):
#         return {"id": str(obj.sender.id), "first_name": obj.sender.first_name}

#     def get_reciever(self, obj):
#         return {"id": str(obj.reciever.id), "first_name": obj.reciever.first_name}
    
#     def get_chat_room(self, obj):
#         return str(obj.chat_room.id)
# """
# class MessageSerializer(serializers.ModelSerializer):
#     sender = UserSerializer(read_only=True)
#     reciever = UserSerializer(read_only=True)
#     chat_room = ChatRoomSerializer(read_only=True)
    

#     class Meta:
#         model = Message
#         fields = "__all__"
    

# class MessageSerializer(serializers.ModelSerializer):
#     sender = serializers.SerializerMethodField()
#     reciever = serializers.SerializerMethodField()
#     chat_room = serializers.SerializerMethodField()

#     class Meta:
#         model = Message
#         fields = (
#             "id",
#             "chat_room",
#             "sender",
#             "reciever",
#             "message",
#         )

#     def get_chat_room(self, obj):
#         return str(obj.chat_room.id)

#     def get_sender(self, obj):
#         return UserSerializer(obj.sender).data

#     def get_reciever(self, obj):
#         return UserSerializer(obj.reciever).data
    
# """

