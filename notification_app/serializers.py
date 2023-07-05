from rest_framework import serializers
from .models import MatchNotification, ResolveChildNotification, DropChildNotification, OrgVerifyNotification, ContactUs, FeedbackReview
from lostchildren.serializers import MatchingChildSerializer
from login_app.serializers import UserSerializer


class MatchNotificationSerializer(serializers.ModelSerializer):
    # matching_child = MatchingChildSerializer()
    matching_child = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    lost_child = serializers.SerializerMethodField()

    class Meta:
        model = MatchNotification
        fields = "__all__"

    def get_matching_child(self, obj):
        return {"id": str(obj.matching_child.id), "recieved_child_id": str(obj.matching_child.recieved_child.id)}

    def get_user(self, obj):
        return {"id": str(obj.user.id)}

    def get_lost_child(self, obj):
        return {"id": str(obj.lost_child.id), "child_name": obj.lost_child.child_name,
                "image": obj.lost_child.image.url}


class SimpeMatchNotificationSerializer(serializers.ModelSerializer):
    # matching_child = MatchingChildSerializer(read_only=True)
    matching_child = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    lost_child = serializers.SerializerMethodField()

    class Meta:
        model = MatchNotification
        fields = "__all__"

    def get_matching_child(self, obj):
        return {"id": str(obj.matching_child.id), "recieved_child_id": str(obj.matching_child.recieved_child.id)}

    def get_user(self, obj):
        return {"id": str(obj.user.id)}

    def get_lost_child(self, obj):
        return {"id": str(obj.lost_child.id), "child_name": obj.lost_child.child_name, "image": obj.lost_child.image.url}


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
    
class ResolveChildNotificationSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    lost_child = serializers.SerializerMethodField()

    class Meta:
        model = ResolveChildNotification
        fields = "__all__"

    def get_user(self, obj):
        return {"id": str(obj.user.id)}

    def get_lost_child(self, obj):
        return {"id": str(obj.lost_child.id)}


class OrgVerifyNotificationSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    org_user = serializers.SerializerMethodField()

    class Meta:
        model = OrgVerifyNotification
        fields = "__all__"

    def get_user(self, obj):
        return {"id": str(obj.user.id)}

    def get_org_user(self, obj):
        return {"id": str(obj.org_user.id), "first_name": obj.org_user.first_name, "last_name": obj.org_user.last_name}


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'message']


class FeedbackReviewSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = FeedbackReview
        fields = "__all__"
