from django.db import models
from baseModel.base_model import BaseModel
from login_app.models import User 
from uuid import uuid4


class Notification(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, related_name="notification", on_delete=models.CASCADE)
    type = models.CharField(max_length=255, choices=[('match_found', 'Match Found'), ('other', 'Other')], default="match_found")
    description = models.TextField(blank=True, null=True)
    
    
    def __str__(self):
        return self.type