'''from django.db import models
from LoginApp.models import User
from baseModel.base_model import BaseModel
# Create your models here.
        
class ChatThread(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_user_msg')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_user_msg')
    
    
    def __str__(self):
        return self.sender.email

class Message(BaseModel):
    message = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_of_msg')
    timestamp = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="message_thread")
    
    def __str__(self):
        return self.message
 
    class Meta:
        ordering = ('timestamp',)


class photos(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None, related_name="attachments")
    images = models.ImageField(blank=True, upload_to='pictures')
'''
from django.db import models
from LoginApp.models import User
from baseModel.base_model import BaseModel
# Create your models here.
        
class ChatThread(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_user_msg')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_user_msg')
    
    
    def __str__(self):
        return self.sender.email

class Message(BaseModel):
    message = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_of_msg')
    timestamp = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="message_thread")
    
    def __str__(self):
        return self.message
 
    class Meta:
        ordering = ('timestamp',)


class photos(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None, related_name="attachments")
    images = models.ImageField(blank=True, upload_to='pictures')
