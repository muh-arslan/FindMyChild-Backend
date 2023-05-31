from django.db import models
from baseModel.base_model import BaseModel
from login_app.models import User 
from uuid import uuid4

class GenericFileUpload(models.Model):
    file_upload = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_upload}"


class ChatRoom(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    users = models.ManyToManyField(User, related_name="chat_room")    
    # room_name = models.CharField(max_length=255, null=True, blank=True)

    # def __str__(self):
    #     return self.room_name
    

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        User, related_name="message_sender", on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, related_name="message", on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"message between {self.sender.email} and {self.reciever.email}"

    class Meta:
        ordering = ("createdAt",)


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message, related_name="message_attachments", on_delete=models.CASCADE)
    attachment = models.ForeignKey(
        GenericFileUpload, related_name="message_uploads", on_delete=models.CASCADE)
    caption = models.CharField(max_length=255, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("createdAt",)
