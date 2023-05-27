from channels.generic.websocket import AsyncJsonWebsocketConsumer
from login_app.models import User
from .models import DropChildNotification
from .serializers import DropChildNotificationSerializer
from chat_app.models import ChatRoom, Message
from chat_app.serializers import ChatRoomSerializer, MessageSerializer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None

    async def connect(self):
        try:
            self.user = self.scope["user"]
            #print(self.user)
            if not self.user.is_authenticated:
                print("user not authenticated")
                return 
        except Exception:
            print(Exception)
        if self.user.is_superuser:
            self.user_channel_id = "admin_group"
            await self.channel_layer.group_add(self.user_channel_id, self.channel_name)
        else:            
            self.user_channel_id = str(self.user.id)
            await self.channel_layer.group_add(self.user_channel_id, self.channel_name)
        await self.accept()
        await self.update_online_status(True)
        print("Connected with room:" + self.user_channel_id)
        print("user status: "+ str(self.user.online_status))
        await self.send_json({
            "type": "welcome_message",
            "message": "Connected with room: " + self.user_channel_id
        })       

    async def disconnect(self, code):
        print("Disconnected!")
        await self.update_online_status(False)
        print("user status: "+ str(self.user.online_status))
        return super().disconnect(code)

    async def receive_json(self, content, **kwargs):
        channel_layer = get_channel_layer()
        message_type = content["type"]

        if message_type == "send_chat_message":
            message = await self.create_message(content)
            await self.channel_layer.group_send(
                content["receiver_id"], {
                    "type": "receive_chat_message",
                    "message": message,
                },
            )
        if message_type == "drop_child_request":
            drop_notification = await self.create_drop_child_notification(content)
            print(drop_notification)
            await self.channel_layer.group_send(
                content["user_id"], {
                    "type": "drop_child_request",
                    "message": drop_notification,
                },
            )
        return super().receive_json(content, **kwargs)
    
    @database_sync_to_async
    def create_message(self, content):
        try:
            new_message = Message.objects.create(sender= self.user, reciever_id=content["receiver_id"], message=content["message"], chat_room_id=content["chat_room_id"])
            serialized_message = MessageSerializer(new_message).data
            return serialized_message
        except Exception as e:
            return e
            
    
    @database_sync_to_async
    def create_drop_child_notification(self, content):
        try:
            drop_notification = DropChildNotification.objects.create(type= content["type"], description=content["description"],user_id = content["user_id"], found_child_id = content["found_child_id"]  )
            serialized_notification = DropChildNotificationSerializer(drop_notification).data
            return serialized_notification
        except Exception as e:
            return Exception(e)
        
    @database_sync_to_async
    def update_online_status(self, value):
        self.user.online_status = value
        self.user.save(update_fields=['online_status'])

    async def match_found(self, event):
        print(event)
        await self.send_json(event)

    async def verification_request(self, event):
        print(event)
        await self.send_json(event)

    async def drop_child_request(self, event):
        print(event)
        await self.send_json(event)
        
    
    async def verification_success(self, event):
        print(event)
        await self.send_json(event)

    async def drop_child_success(self, event):
        print(event)
        await self.send_json(event)

    # @database_sync_to_async
    # def get_serialized_message(self):
    #     messages = self.chat_room.message.all().order_by("updated_at")[0:50]
    #     #print(messages)
    #     return MessageSerializer(messages, many=True).data
        
    async def receive_chat_message(self, event):
        print(event)
        await self.send_json(event)