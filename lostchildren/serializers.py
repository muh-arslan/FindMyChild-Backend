from rest_framework import serializers
from .models import LostChild, FoundChild


class BaseChildSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        exclude = ['image_encoding']
        # fields = '__all__'

    def create(self, validated_data):
        # Create the child object
        child = super().create(validated_data)
        # Generate the face encodings for the child
        child.generate_face_encodings()
        # Save the child object
        child.save()
        # Return the child object
        return child


class LostChildSerializer(BaseChildSerializer):
    class Meta(BaseChildSerializer.Meta):
        model = LostChild


class FoundChildSerializer(BaseChildSerializer):
    class Meta(BaseChildSerializer.Meta):
        model = FoundChild


class ReceivedChildrenSerializer(BaseChildSerializer):
    reporter = serializers.SerializerMethodField()
    
    class Meta(BaseChildSerializer.Meta):
        model = FoundChild

    def get_reporter(self, obj):
        return {"OrgName": obj.reporter.first_name, "OrgId": obj.reporter.id}
    
