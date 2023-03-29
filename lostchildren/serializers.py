from rest_framework import serializers
from .models import LostChild


class LostChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostChild
        fields = '__all__'

    def create(self, validated_data):
        # Create the child object
        child = super().create(validated_data)
        # Generate the face encodings for the child
        child.generate_face_encodings()
        # Save the child object
        child.save()
        # Return the child object
        return child
