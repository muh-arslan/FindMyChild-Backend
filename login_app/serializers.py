from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiParameter, OpenApiExample
from .models import(
    User, AgencyProfile, AppUserProfile, Role
)
from django.contrib.auth.models import Group
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
            role = validated_data.get("role", None)  # Get the role from validated_data
            user = User.objects.create(**validated_data)
            groups = []
            if role == Role.APPUSER:
                groups = [Group.objects.get(name="appUser_group")]
            elif role == Role.AGENCY:
                groups = [Group.objects.get(name="agency_group")]
                user.is_active = False
            # hashing the password for security
            user.set_password(user.password)
            user.save()
            user.groups.set(groups)
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


class AppUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AppUserProfile
        fields = "__all__"


class AgencyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AgencyProfile
        fields = "__all__"


class RequestChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=200)
    new_password = serializers.CharField(max_length=200)
        

class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class SimpleOrgUserSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")