# chat/consumers.py
"""
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

"""
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, ChatRoom
from login_app.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # Get the user with whom the connection is made
        self.other_user_id = self.scope["url_route"]["kwargs"]["other_user_id"]
        self.other_user = User.objects.get(id=self.other_user_id)

        # Create a unique channel name for the user pair
        self.room_name = f"chat_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
        # Join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        
        # Check if the chat Room already exists
        if not ChatRoom.objects.filter(room_name = self.room_group_name).exists():
            data = {}
            data['room_name'] = self.room_group_name
            data['channel_name'] = self.channel_name
            data[self.user.user_type] = self.user
            data[self.other_user.user_type] = self.other_user

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Get the user who sent the message
        user = self.scope["user"]

        # Save the message to the database
        Message.objects.create(user=user, content=message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

"""
"""
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from login_app.models import User
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer


from .models import Connection, Message

class ChatConsumer(AsyncWebsocketConsumer):
    serializer_class = ChatRoomSerializer
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        self.user = self.scope["user"]

        # Get the user with whom the connection is made
        self.other_user_id = self.scope["url_route"]["kwargs"]["other_user_id"]
        self.other_user = User.objects.get(id=self.other_user_id)

        # Create a unique channel name for the user pair
        self.room_name = f"chat_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
        # Join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        
        # Check if the chat Room already exists
        if not ChatRoom.objects.filter(room_name = self.room_group_name).exists():
            chat_room_serializer = self.serializer_class(data=data)
            data = {}
            data['room_name'] = self.room_group_name
            data['channel_name'] = self.channel_name
            data[self.user.user_type] = self.user
            data[self.other_user.user_type] = self.other_user
            if chat_room_serializer.is_valid():
                chat_room_serializer.save()
            else:
                raise Exception("Error validating room")

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        message_type = text_data_json["type"]
        sender = self.scope["user"]
        timestamp = text_data_json["timestamp"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )
        if message_type == "chat":
            await self.save_message(sender, message, timestamp)
        elif message_type == "history":
            await self.send_message_history()

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        timestamp = event["timestamp"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "sender": sender.username, "timestamp": timestamp}))

    @database_sync_to_async
    def save_message(self, sender, message, timestamp):
        connection = Connection.objects.filter(user=sender, room_name=self.room_name)
        if connection:
            Message.objects.create(connection=connection, message=message, sender=sender, timestamp=timestamp)

    @database_sync_to_async
    def get_message_history(self):
        connection = Connection.objects.filter(room_name=self.room_name)
        if connection:
            messages = Message.objects.filter(connection=connection).order_by("timestamp")
            return messages
        else:
            return []

    async def send_message_history(self):
        messages = await self.get_message_history()
        for message in messages:
            await self.send(text_data=json.dumps({"message": message.message, "sender": message.sender.username, "timestamp": message.timestamp}))

"""
   
        # Get the user with whom the connection is made
        #self.other_user_id = self.scope["url_route"]["kwargs"]["other_user_id"]
        #self.other_user = User.objects.get(id=self.other_user_id)

        # Create a unique channel name for the user pair
        #self.room_name = f"chat_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
        # Join room group

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import ChatRoom, Message
from login_app.models import User
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from .serializers import MessageSerializer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None

    async def connect(self):
        self.user = self.scope["user"]
        #print(self.user)
        if not self.user.is_authenticated:
            print("user not authenticated")
            return 
        await self.accept()
        self.room_id = f"{self.scope['url_route']['kwargs']['room_id']}"
        try:
            self.chat_room = await sync_to_async(ChatRoom.objects.get)(id=self.room_id)
        except Exception:
            raise Exception("Chat Room did not exists")
        if self.user.user_type == 'appUser':
            self.appUser = self.user
            orgUser_id = self.chat_room.orgUser_id
            self.orgUser = await sync_to_async(User.objects.get)(id=orgUser_id)
        else:
            appUser_id = self.chat_room.appUser_id
            self.appUser = await sync_to_async(User.objects.get)(id=appUser_id)
            self.orgUser = self.user
        print(">>>>>>>>>>>>>>>>>>>orgUser")
        print(self.appUser.id)
        print(">>>>>>>>>>>>>>>>>>>orgUser")
        print(self.orgUser.id)
        self.room_name = self.chat_room.room_name
     
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        print("Connected with room:" + self.room_name)
        #await self.get_serialized_message()
        #await self.accept()
        #messages = await sync_to_async(self.chat_room.message.all().order_by)("-updated_at")[0:50]
        #messages = await sync_to_async(list)(self.chat_room.message.all().order_by("-updated_at")[:50])

        await self.send_json({
            "type": "last_50_messages",
            "messages": await self.get_serialized_message()
        })
       

    async def disconnect(self, code):
        print("Disconnected!")
        return super().disconnect(code)

    async def receive_json(self, content, **kwargs):
        message_type = content["type"]
        if message_type == "greeting":
            await self.send_json({
                "type": "greeting_response",
                "message": "How are you?",
            })
        if message_type == "chat_message":
            message = await self.create_message(content)
            print(message)
            await self.channel_layer.group_send(
                self.room_name, {
                    "type": "chat_message_echo",
                    "message": message,
                },
            )
        return super().receive_json(content, **kwargs)
    
    @database_sync_to_async
    def create_message(self, content):
        data = {
            "sender": self.user,
            'reciever':self.get_receiver(),
            'message':content["message"],
            'chat_room':self.chat_room
        }
        serialized_message = MessageSerializer(data = data)
        if serialized_message.is_valid():
            serialized_message.save(sender = self.user,
            reciever = self.get_receiver(),
            chat_room = self.chat_room)
            return serialized_message.data
        
    @database_sync_to_async
    def get_serialized_message(self):
        messages = self.chat_room.message.all().order_by("updated_at")[0:50]
        #print(messages)
        return MessageSerializer(messages, many=True).data
        
    
    def get_receiver(self):
        if self.user.id != self.appUser.id:
            return self.appUser
        return self.orgUser
        
    async def chat_message_echo(self, event):
        print(event)
        await self.send_json(event)