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
    orgUser = models.ForeignKey(User, related_name="chat_org_user", on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255, null=True, blank=True)
    channel_name = models.CharField(max_length=255, null=True, blank=True)
    appUser = models.ForeignKey(User, related_name="chat_app_user", on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.room_name
    

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender = models.ForeignKey(
        User, related_name="message_sender", on_delete=models.CASCADE)
    reciever = models.ForeignKey(
        User, related_name="message_reciever", on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, related_name="message", on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"message between {self.sender.email} and {self.reciever.email}"

    class Meta:
        ordering = ("-created_at",)


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message, related_name="message_attachments", on_delete=models.CASCADE)
    attachment = models.ForeignKey(
        GenericFileUpload, related_name="message_uploads", on_delete=models.CASCADE)
    caption = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
