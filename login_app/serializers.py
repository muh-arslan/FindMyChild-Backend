from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiParameter, OpenApiExample
from .models import(
    User,
)
from django.db import models
from django.core import validators

class UserSerializer(serializers.ModelSerializer):
    
    # adding an extra field to serializers to validate password
    confirmPassword = serializers.CharField(max_length=200, write_only=True)
    
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}
        
    # Overwriting the create method for password validation check
    def create(self, validated_data):
        if validated_data['confirmPassword'] == validated_data['password']:
            # deleting the 'confirmPassword' key from dict 'validated_data' so user can be created
            del validated_data['confirmPassword']
            user = User.objects.create(**validated_data)
            # hashing the password for security
            user.set_password(user.password)
            user.is_staff = True
            user.save()
            return user
        else:
            raise serializers.ValidationError({'Password': 'Passwords did not match'})
    
    def validate_email(self, value):
        try:
            validators.validate_email(value)
        except validators.ValidationError:
            raise serializers.ValidationError("Invalid email")
        
        # Check if the email is already registered
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        
        return value
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=200)
    

class RequestChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=200)
    new_password = serializers.CharField(max_length=200)
        

class FavoriteSerializer(serializers.Serializer):
    favorite_id = serializers.IntegerField()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()