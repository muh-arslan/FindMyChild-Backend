import json
from django.db import models
from django.utils import timezone
from uuid import uuid4
from .face_recognition import feature_extraction
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
    child_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    mother_name = models.CharField(max_length=50)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices, null=True)
    age = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=15, null=True)
    email = models.EmailField(null=True)
    description = models.TextField()

    class Meta:
        abstract = True


class LostChild(BaseModel):
    date_of_lost = models.DateField(default=timezone.now)
    location_where_lost = models.CharField(max_length=100)
    city = models.CharField(max_length=50, null=True)
    provinces_choices = [('AJK', 'Azad Jammu and Kashmir'),    ('Bal', 'Balochistan'),    (
        'GB', 'Gilgit Baltistan'),    ('KP', 'Khyber Pakhtunkhwa'),    ('Pun', 'Punjab'),    ('Snd', 'Sindh')]
    province = models.CharField(
        max_length=18, choices=provinces_choices, null=True)
    home_address = models.CharField(max_length=100, null=True)
    image1 = models.ImageField(
        upload_to=get_child_image_upload_path_lost_child)
    image2 = models.ImageField(
        upload_to=get_child_image_upload_path_lost_child, blank=True)
    image3 = models.ImageField(
        upload_to=get_child_image_upload_path_lost_child, blank=True)
    image_encoding1 = models.JSONField(null=True, blank=True)
    image_encoding2 = models.JSONField(null=True, blank=True)
    image_encoding3 = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BaseModel.STATUS_CHOICES, default='lost')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lostReport', to_field='id')

    def generate_face_encodings(self):
        image_paths = [self.image1.path]
        if self.image2:
            image_paths.append(self.image2.path)
        if self.image3:
            image_paths.append(self.image3.path)

        encodings = []
        for path in image_paths:
            encoding = feature_extraction(path)
            encodings.append(encoding.tolist())

        if len(encodings) >= 1:
            self.image_encoding1 = json.dumps(encodings[0])
        if len(encodings) >= 2:
            self.image_encoding2 = json.dumps(encodings[1])
        if len(encodings) >= 3:
            self.image_encoding3 = json.dumps(encodings[2])


class FoundChild(BaseModel):
    date_of_found = models.DateField(default=timezone.now)
    location_where_found = models.CharField(max_length=100)
    image1 = models.ImageField(
        upload_to=get_child_image_upload_path_found_child)
    image2 = models.ImageField(
        upload_to=get_child_image_upload_path_found_child, blank=True)
    image3 = models.ImageField(
        upload_to=get_child_image_upload_path_found_child, blank=True)
    image_encoding1 = models.JSONField(null=True, blank=True)
    image_encoding2 = models.JSONField(null=True, blank=True)
    image_encoding3 = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BaseModel.STATUS_CHOICES, default='found')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='foundReport', to_field='id')

    def generate_face_encodings(self):
        image_paths = [self.image1.path]
        if self.image2:
            image_paths.append(self.image2.path)
        if self.image3:
            image_paths.append(self.image3.path)

        encodings = []
        for path in image_paths:
            encoding = feature_extraction(path)
            encodings.append(encoding.tolist())

        if len(encodings) >= 1:
            self.image_encoding1 = json.dumps(encodings[0])
        if len(encodings) >= 2:
            self.image_encoding2 = json.dumps(encodings[1])
        if len(encodings) >= 3:
            self.image_encoding3 = json.dumps(encodings[2])
