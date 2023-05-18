# chat/consumers.py

   
        # Get the user with whom the connection is made
        #self.other_user_id = self.scope["url_route"]["kwargs"]["other_user_id"]
        #self.other_user = User.objects.get(id=self.other_user_id)

        # Create a unique channel name for the user pair
        #self.room_name = f"chat_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
        # Join room group

from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from .models import ChatRoom, Message
from login_app.models import User
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
# from .serializers import MessageSerializer


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
        # self.room_id = f"{self.scope['url_route']['kwargs']['room_id']}"
        # try:
        #     self.chat_room = await sync_to_async(ChatRoom.objects.get)(id=self.room_id)
        # except Exception:
        #     raise Exception("Chat Room did not exists")
        # if self.user.user_type == 'appUser':
        #     self.appUser = self.user
        #     orgUser_id = self.chat_room.orgUser_id
        #     self.orgUser = await sync_to_async(User.objects.get)(id=orgUser_id)
        # else:
        #     appUser_id = self.chat_room.appUser_id
        #     self.appUser = await sync_to_async(User.objects.get)(id=appUser_id)
        #     self.orgUser = self.user
        # print(">>>>>>>>>>>>>>>>>>>orgUser")
        # print(self.appUser.id)
        # print(">>>>>>>>>>>>>>>>>>>orgUser")
        # print(self.orgUser.id)
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
        print(channel_layer)
    #     message_type = content["type"]
    #     if message_type == "greeting":
    #         await self.send_json({
    #             "type": "greeting_response",
    #             "message": "How are you?",
    #         })
    #     if message_type == "chat_message":
    #         message = await self.create_message(content)
    #         print(message)
    #         await self.channel_layer.group_send(
    #             self.room_name, {
    #                 "type": "chat_message_echo",
    #                 "message": message,
    #             },
    #         )
    #     return super().receive_json(content, **kwargs)
    
    # @database_sync_to_async
    # def create_message(self, content):
    #     data = {
    #         "sender": self.user,
    #         'reciever':self.get_receiver(),
    #         'message':content["message"],
    #         'chat_room':self.chat_room
    #     }
    #     serialized_message = MessageSerializer(data = data)
    #     if serialized_message.is_valid():
    #         serialized_message.save(sender = self.user,
    #         reciever = self.get_receiver(),
    #         chat_room = self.chat_room)
    #         return serialized_message.data
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
    
    async def verification_success(self, event):
        print(event)
        await self.send_json(event)

    # @database_sync_to_async
    # def get_serialized_message(self):
    #     messages = self.chat_room.message.all().order_by("updated_at")[0:50]
    #     #print(messages)
    #     return MessageSerializer(messages, many=True).data
        
    
    # def get_receiver(self):
    #     if self.user.id != self.appUser.id:
    #         return self.appUser
    #     return self.orgUser
        
    # async def chat_message_echo(self, event):
    #     print(event)
    #     await self.send_json(event)