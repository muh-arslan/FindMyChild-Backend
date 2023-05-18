from rest_framework import serializers
from login_app.models import(
    User, OrgDetails
)

class SimpleOrgUserSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")
    