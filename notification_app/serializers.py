from rest_framework import serializers
from .models import MatchNotification, DropChildNotification
from lostchildren.serializers import MatchingChildSerializer

class MatchNotificationSerializer(serializers.ModelSerializer):
    matching_child = MatchingChildSerializer()
    # matching_child = serializers.SerializerMethodField()    
    user = serializers.SerializerMethodField()
    lost_child = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchNotification
        fields = "__all__"

    def get_matching_child(self, obj):
        return {"id": str(obj.matching_child.id)}
    
    def get_user(self, obj):
        return {"id": str(obj.user.id)}
    
    def get_lost_child(self, obj):
        return {"id": str(obj.lost_child.id), "child_name": obj.lost_child.child_name}

class DropChildNotificationSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    found_child = serializers.SerializerMethodField()
    
    class Meta:
        model = DropChildNotification
        fields = "__all__"

    def get_user(self, obj):
        return {"id": str(obj.user.id)}
    
    def get_found_child(self, obj):
        return {"id": str(obj.found_child.id)}


