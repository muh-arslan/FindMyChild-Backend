from django.db import models
from baseModel.base_model import BaseModel
from login_app.models import User
from lostchildren.models import MatchingChild, LostChild, FoundChild
from uuid import uuid4


class Notification(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    is_seen = models.BooleanField(default=False)
    is_opened = models.BooleanField(default=False)

    class Meta:
        abstract = True


class MatchNotification(Notification):
    type = models.CharField(max_length=100, default="match_found", blank=True)
    user = models.ForeignKey(
        User, related_name="match_notification", on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    lost_child = models.ForeignKey(
        LostChild, on_delete=models.CASCADE, related_name="match_notification")
    matching_child = models.ForeignKey(
        MatchingChild, related_name="notification", on_delete=models.CASCADE)

    def __str__(self):
        return self.type


class DropChildNotification(Notification):
    type = models.CharField(max_length=100, choices=[(
        'drop_child_request', 'Drop Child Request'), ('drop_child_success', 'Drop Child Success')])
    user = models.ForeignKey(
        User, related_name="drop_notification", on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    found_child = models.ForeignKey(
        FoundChild, on_delete=models.CASCADE, related_name="drop_notification")

    def __str__(self):
        return self.type


class OrgVerifyNotification(Notification):
    type = models.CharField(max_length=100, choices=[(
        'verification_request', 'Verification Request'), ('verification_success', 'Verification Success')])
    user = models.ForeignKey(
        User, related_name="user_verify_nofication", on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    org_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="org_user_verify_nofication")

    def __str__(self):
        return self.type


class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name


class FeedbackReview(models.Model):
    user = models.ForeignKey(
        User, related_name="user_feedback", on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback = models.TextField()

    def __str__(self):
        return f"Rating: {self.rating} - Feedback: {self.feedback}"
