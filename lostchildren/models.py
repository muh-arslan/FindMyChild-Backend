import json
import numpy as np
from django.db import models
from django.utils import timezone
from uuid import uuid4
from .face_recognizer import feature_extractor
from login_app.models import User


def get_child_image_upload_path_lost_child(instance, filename):
    return f"Children/lost_children_images/{instance.id}/{filename}"


def get_child_image_upload_path_found_child(instance, filename):
    return f"Children/found_children_images/{instance.id}/{filename}"


class BaseModel(models.Model):
    STATUS_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('received', 'Received'),
        ('resolved', 'Resolved')
    ]
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    child_name = models.CharField(max_length=50, null=True, blank=True)
    father_name = models.CharField(max_length=50, null=True, blank=True)
    mother_name = models.CharField(max_length=50, null=True, blank=True)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(
        max_length=1, choices=gender_choices, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class LostChild(BaseModel):
    date_of_lost = models.DateField(null=True, blank=True)
    location_where_lost = models.CharField(
        max_length=100, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    provinces_choices = [('AJK', 'Azad Jammu and Kashmir'),    ('Bal', 'Balochistan'),    (
        'GB', 'Gilgit Baltistan'),    ('KP', 'Khyber Pakhtunkhwa'),    ('Pun', 'Punjab'),    ('Snd', 'Sindh')]
    province = models.CharField(
        max_length=18, choices=provinces_choices, null=True, blank=True)
    home_address = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(
        upload_to=get_child_image_upload_path_lost_child, null=True, blank=True)
    image_encoding = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=BaseModel.STATUS_CHOICES, default='lost')
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lostReport', to_field='id')

    def generate_face_encodings(self):
        if self.image:
            image_path = self.image.path
            encoding = feature_extractor(image_path)
            if encoding is not None:
                self.image_encoding = json.dumps(np.asarray(encoding).tolist())


class FoundChild(BaseModel):
    date_of_found = models.DateField(null=True, blank=True)
    location_where_found = models.CharField(
        max_length=100, null=True, blank=True)
    image = models.ImageField(
        upload_to=get_child_image_upload_path_found_child, null=True, blank=True)
    image_encoding = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=BaseModel.STATUS_CHOICES, default='found')
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='foundReport', to_field='id')

    def generate_face_encodings(self):
        if self.image:
            image_path = self.image.path
            encoding = feature_extractor(image_path)
            if encoding is not None:
                self.image_encoding = json.dumps(np.asarray(encoding).tolist())
