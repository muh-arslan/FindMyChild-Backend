from django.db import models
from LoginApp.models import User
from baseModel.base_model import BaseModel

# Create your models here.

class FriendList(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="friends")
    friends = models.ManyToManyField(User, blank=True)
    
    def __str__(self):
        return self.user.email

class FriendRequest(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receive")
    timestamp = models.DateTimeField(auto_now_add=True)