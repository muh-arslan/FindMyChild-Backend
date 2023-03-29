import face_recognition
import json

from django.db import models
from django.db.models import JSONField, UUIDField
from uuid import uuid4


def get_child_image_upload_path(instance, filename):
    return f"children_images/{instance.id}/{filename}"


class BaseChild(models.Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50)
    mother_name = models.CharField(max_length=50)
    image1 = models.ImageField(upload_to=get_child_image_upload_path)
    image2 = models.ImageField(
        upload_to=get_child_image_upload_path, blank=True)
    image3 = models.ImageField(
        upload_to=get_child_image_upload_path, blank=True)
    image_encoding1 = JSONField(null=True, blank=True)
    image_encoding2 = JSONField(null=True, blank=True)
    image_encoding3 = JSONField(null=True, blank=True)
    date_of_lost = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

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


class LostChild(BaseChild):
    date_of_lost = models.DateField()
    location = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    description = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class FoundChild(BaseChild):
    date_of_found = models.DateField(null=True, blank=True)
    found_location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
