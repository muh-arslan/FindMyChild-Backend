from rest_framework import serializers
from .models import LostChild, FoundChild, ReceivedChild,MatchingChild, Report, Status


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        # exclude = ['image_encoding']
        fields = '__all__'

    def create(self, validated_data):
        # Create the child object
        status = validated_data.get("status", None) 
        if status == Status.Lost:
            child = LostChild.objects.create(**validated_data)
        
        if status == Status.Found:
            child = FoundChild.objects.create(**validated_data)

        if status == Status.Received:
            child = ReceivedChild.objects.create(**validated_data)
        # Generate the face encodings for the child
        child.generate_face_encodings()
        # Save the child object
        child.save()
        # Return the child object
        return child


# class LostChildSerializer(BaseChildSerializer):
#     class Meta(BaseChildSerializer.Meta):
#         model = LostChild


# class FoundChildSerializer(BaseChildSerializer):
#     # reporter = serializers.SerializerMethodField()
#     class Meta(BaseChildSerializer.Meta):
#         model = FoundChild

#     # def get_reporter(self, obj):
#     #     return {"OrgName": obj.reporter.first_name, "OrgId": str(obj.reporter.id)}

class ReceivedChildrenSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()
    
    class Meta:
        model = ReceivedChild
        fields = '__all__'

    def get_reporter(self, obj):
        return {"OrgName": obj.reporter.first_name, "OrgId": obj.reporter.id}
    

class MatchingChildSerializer(serializers.ModelSerializer):
    recieved_child = ReportSerializer()

    class Meta:
        model = MatchingChild
        fields = '__all__'


# class MatchingReportsSerializer(serializers.ModelSerializer):
#     lost_child = LostChildSerializer()
#     reports = MatchingChildSerializer(many=True)

#     class Meta:
#         model = MatchingReports
#         fields = '__all__'
