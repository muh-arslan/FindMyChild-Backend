import json
import numpy as np
from django.db import models
from django.utils import timezone
from uuid import uuid4
from .face_recognizer import feature_extractor
from login_app.models import User

def get_child_image_upload_path(instance, filename):
    if(instance.status == Status.Lost):
        return f"Children/lost_children_images/{instance.id}/{filename}"
    if(instance.status == Status.Found):
        return f"Children/found_children_images/{instance.id}/{filename}"    
    if(instance.status == Status.Received):
        return f"Children/received_children_images/{instance.id}/{filename}"
    

class Status(models.TextChoices):
        Lost = 'lost', 'Lost',
        Found = 'found', 'Found',
        Received = 'received', 'Received',
        Resolved = 'resolved', 'Resolved'


class Report(models.Model):  

    provinces_choices = [('AJK', 'Azad Jammu and Kashmir'),    ('Bal', 'Balochistan'),    (
        'GB', 'Gilgit Baltistan'),    ('KP', 'Khyber Pakhtunkhwa'),    ('Pun', 'Punjab'),    ('Snd', 'Sindh')]
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    base_status = Status.Lost
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    child_name = models.CharField(max_length=50, null=True, blank=True)
    father_name = models.CharField(max_length=50, null=True, blank=True)
    mother_name = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=gender_choices, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    province = models.CharField(
        max_length=18, choices=provinces_choices, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    location = models.CharField(
        max_length=100, null=True, blank=True)
    home_address = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(
        upload_to=get_child_image_upload_path, null=True, blank=True)
    image_encoding = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices)
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='report')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_face_encodings(self):
        print("generating face encodings!")
        if self.image:
            image_path = self.image.path
            encoding = feature_extractor(image_path)
            # print(encoding)
            if encoding is not None:
                self.image_encoding = json.dumps(np.asarray(encoding).tolist())

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         # self.status = self.base_status
    #         print("maannnnnnn")
    #         return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.child_name

class LostChildManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(status=Status.Lost)
    
class LostChild(Report):

    objects = LostChildManager()
    base_status = Status.Lost
    
    class Meta:
        proxy = True
    

class FoundChildManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(status=Status.Found)
    
class FoundChild(Report):
    
    objects = FoundChildManager()
    base_status = Status.Found

    class Meta:
        proxy = True
    
    
class ReceivedChildManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(status = Status.Received)
    
class ReceivedChild(Report):
    
    objects = ReceivedChildManager()
    base_status = Status.Received

    class Meta:
        proxy = True

class MatchingChild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    lost_child = models.ForeignKey(
        LostChild, on_delete=models.CASCADE, related_name="matching_child")
    recieved_child = models.ForeignKey(
        ReceivedChild, on_delete=models.CASCADE, related_name="match")
    distance = models.FloatField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.recieved_child.child_name


"""
class MatchingReports(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    lost_child = models.OneToOneField(
        LostChild, on_delete=models.CASCADE, related_name="matchingReports")
    reports = models.ManyToManyField(MatchingChild, related_name="matches")
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.lost_child.child_name

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
    provinces_choices = [('AJK', 'Azad Jammu and Kashmir'),    ('Bal', 'Balochistan'),    (
        'GB', 'Gilgit Baltistan'),    ('KP', 'Khyber Pakhtunkhwa'),    ('Pun', 'Punjab'),    ('Snd', 'Sindh')]
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    child_name = models.CharField(max_length=50, null=True, blank=True)
    father_name = models.CharField(max_length=50, null=True, blank=True)
    mother_name = models.CharField(max_length=50, null=True, blank=True)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(
        max_length=1, choices=gender_choices, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    province = models.CharField(
        max_length=18, choices=provinces_choices, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LostChild(BaseModel):
    date_of_lost = models.DateField(null=True, blank=True)
    location_where_lost = models.CharField(
        max_length=100, null=True, blank=True)
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

    def __str__(self):
        return self.child_name


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

    def __str__(self):
        return self.child_name
"""