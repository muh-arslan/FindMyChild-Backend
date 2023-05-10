from django.db import models
from baseModel.base_model import BaseModel
from login_app.models import User
from lostchildren.models import MatchingChild, LostChild
from uuid import uuid4


class MatchNotification(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, related_name="notification", on_delete=models.CASCADE)
    type = models.CharField(max_length= 100, default="match_found", blank=True)
    description = models.TextField(blank=True, null=True)
    lost_child = models.ForeignKey(LostChild, on_delete=models.CASCADE, related_name="notification")
    matching_child = models.ForeignKey(MatchingChild, related_name="notification", on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.type