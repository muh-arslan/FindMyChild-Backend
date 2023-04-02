import face_recognition
import json
import os

from django.db import models
from django.db.models import JSONField, UUIDField
from uuid import uuid4


def get_child_image_upload_path_lost_child(instance, filename):
    return f"lost_children_images/{instance.id}/{filename}"


def get_child_image_upload_path_found_child(instance, filename):
    return f"found_children_images/{instance.id}/{filename}"


class LostChild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    mother_name = models.CharField(max_length=50)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices, null=True)
    age = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=11, null=True)
    location_where_lost = models.CharField(max_length=100)
    city = models.CharField(max_length=50, null=True)
    province = models.CharField(max_length=50, null=True)
    home_address = models.CharField(max_length=100, null=True)
    date_of_lost = models.DateField()
    description = models.TextField()
    image1 = models.ImageField(
        upload_to=get_child_image_upload_path_lost_child)
    image2 = models.ImageField(
        upload_to=get_child_image_upload_path_lost_child, blank=True)
    image3 = models.ImageField(
        upload_to=get_child_image_upload_path_lost_child, blank=True)
    image_encoding1 = models.JSONField(null=True, blank=True)
    image_encoding2 = models.JSONField(null=True, blank=True)
    image_encoding3 = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def generate_face_encodings(self):
        image_paths = [self.image1.path]
        if self.image2:
            image_paths.append(self.image2.path)
        if self.image3:
            image_paths.append(self.image3.path)

        encodings = []
        for path in image_paths:
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(image)[0]
            encodings.append(encoding.tolist())

        if len(encodings) >= 1:
            self.image_encoding1 = json.dumps(encodings[0])
        if len(encodings) >= 2:
            self.image_encoding2 = json.dumps(encodings[1])
        if len(encodings) >= 3:
            self.image_encoding3 = json.dumps(encodings[2])


class FoundChild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    mother_name = models.CharField(max_length=50)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices, null=True)
    age = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=11, null=True)
    location_where_found = models.CharField(max_length=100)
    city = models.CharField(max_length=50, null=True)
    province = models.CharField(max_length=50, null=True)
    home_address = models.CharField(max_length=100, null=True)
    date_of_lost = models.DateField()
    description = models.TextField()
    image1 = models.ImageField(
        upload_to=get_child_image_upload_path_found_child)
    image2 = models.ImageField(
        upload_to=get_child_image_upload_path_found_child, blank=True)
    image3 = models.ImageField(
        upload_to=get_child_image_upload_path_found_child, blank=True)
    image_encoding1 = models.JSONField(null=True, blank=True)
    image_encoding2 = models.JSONField(null=True, blank=True)
    image_encoding3 = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def generate_face_encodings(self):
        image_paths = [self.image1.path]
        if self.image2:
            image_paths.append(self.image2.path)
        if self.image3:
            image_paths.append(self.image3.path)

        encodings = []
        for path in image_paths:
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(image)[0]
            encodings.append(encoding.tolist())

        if len(encodings) >= 1:
            self.image_encoding1 = json.dumps(encodings[0])
        if len(encodings) >= 2:
            self.image_encoding2 = json.dumps(encodings[1])
        if len(encodings) >= 3:
            self.image_encoding3 = json.dumps(encodings[2])
