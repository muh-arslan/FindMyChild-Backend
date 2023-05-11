import json
import numpy as np
from collections import OrderedDict
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from findmychild.custom_methods import IsAuthenticatedCustom
from rest_framework.response import Response
from .models import LostChild, FoundChild, MatchingReports, MatchingChild
from .serializers import LostChildSerializer, FoundChildSerializer, ReceivedChildrenSerializer, MatchingChildSerializer, MatchingReportsSerializer
from .face_recognizer import feature_extractor, match_results
from django.forms.models import model_to_dict
from login_app.models import User
from notification_app.models import MatchNotification
from notification_app.serializers import MatchNotificationSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class LostChildList(viewsets.ModelViewSet):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = LostChild.objects.all()
    serializer_class = LostChildSerializer


class FoundChildList(viewsets.ModelViewSet):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = FoundChild.objects.all()
    serializer_class = FoundChildSerializer

class LostChildCreate(generics.CreateAPIView):
    serializer_class = LostChildSerializer
    # permission_classes = (IsAuthenticatedCustom, )

    def post(self, request, format=None):
        # user = request.user
        # get id of the FoundChild or LostChild object
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        child = serializer.save()

        queryset = FoundChild.objects.filter(status='received')

        image_encoding = np.array(json.loads(child.image_encoding))

        # iterate through all reports and check for matching faces
        try:
            matchingReports_obj = child.matchingReports
        except Exception:
            matchingReports_obj = MatchingReports.objects.create(lostChild=child)
        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None

            if child.gender == report.gender:
                print(report.child_name)
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
                    
                    match_obj = {
                        "recieved_child": model_to_dict(report),
                        "distance": distance
                    }
                    serialized_report = MatchingChildSerializer(data = match_obj)
                    if serialized_report.is_valid(raise_exception= True):
                        matching_child_obj = serialized_report.save(recieved_child=report)
                        notification = MatchNotification.objects.create(user=report.reporter,
                            lost_child=child,
                            matching_child=matching_child_obj)
                        serialized_notification = MatchNotificationSerializer(notification).data
                        async_to_sync(self.channel_layer.group_send)(
                            f"{report.reporter_id}",
                            {
                                "type": "match_found",
                                "message": serialized_notification["id"],
                            },
                        )
                        matchingReports_obj.reports.add(matching_child_obj)

        output_data = MatchingReportsSerializer(matchingReports_obj).data

        return Response(output_data)
    
class UpdateChildStatus(generics.CreateAPIView):
    serializer_class = FoundChildSerializer
    channel_layer = get_channel_layer()

    def post(self, request, format=None):
        # get id of the FoundChild or LostChild object
        report_id = request.data.get('report_id', None)
        org_user_id = request.data.get('org_user_id', None)
        if not report_id or not org_user_id:
            return Response({'error': 'Object report_id not found'}, status=400)
        report = FoundChild.objects.get(id=report_id)
        orgUser = User.objects.get(id=org_user_id)
        report.reporter = orgUser
        report.status = 'received'
        child = self.serializer_class(report)

        queryset = FoundChild.objects.filter(status='received')

        image_encoding = np.array(json.loads(child.image_encoding))

        # iterate through all reports and check for matching faces
        try:
            matchingReports_obj = child.matchingReports
        except Exception:
            matchingReports_obj = MatchingReports.objects.create(lostChild=child)
        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None

            if child.gender == report.gender:
                print(report.child_name)
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
                    
                    match_obj = {
                        "recieved_child": model_to_dict(child),
                        "distance": distance
                    }
                    serialized_report = MatchingChildSerializer(data = match_obj)
                    if serialized_report.is_valid(raise_exception= True):
                        matching_child_obj = serialized_report.save(recieved_child=report)
                        report.matchingReports.reports.add(matching_child_obj)
                        # async_to_sync(self.channel_layer.group_send)(
                        #     f"{report.id}",
                        #     {
                        #         "type": "match_found",
                        #         "payload": "Match Found",
                        #     },
                        # )

        output_data = MatchingReportsSerializer(matchingReports_obj).data

        return Response(output_data)

class MatchedReports(APIView):
    channel_layer = get_channel_layer()
    def post(self, request, format=None):
        # get id of the FoundChild or LostChild object
        id = request.data.get('id', None)
        if not id:
            return Response({'error': 'Object id not found'}, status=400)

        # check if object exists

        if request.data.get('type') == 'lost':
            flag = True
            try:
                child = LostChild.objects.get(id=id)
                queryset = FoundChild.objects.all()
                #queryset = FoundChild.objects.filter(status='received')
            except FoundChild.DoesNotExist:
                return Response({'error': 'No Received Reports Found to Match with'}, status=404)

        # if request.data.get('type') == 'found':
        #     flag = False
        #     try:
        #         child = FoundChild.objects.get(id=id)
        #         queryset = LostChild.objects.all()
        #     except LostChild.DoesNotExist:
        #         return Response({'error': 'No Lost Reports Found to Match with'}, status=404)

        # get image encoding of the child
        image_encoding = np.array(json.loads(child.image_encoding))

        # iterate through all reports and check for matching faces
        try:
            matchingReports_obj = child.matchingReports
        except Exception:
            matchingReports_obj = MatchingReports.objects.create(lostChild=child)
        matched_reports = []
        distances = []
        print(image_encoding)
        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None
            if child.gender == report.gender:
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
                    match_obj = {
                        "recieved_child": model_to_dict(report),
                        "distance": distance
                    }
                    serialized_report = MatchingChildSerializer(data = match_obj)
                    serialized_report.is_valid(raise_exception= True)
                    if serialized_report.is_valid():
                        matching_child_obj = serialized_report.save(recieved_child=report)
                        print(model_to_dict(matching_child_obj))
                        matchingReports_obj.reports.add(matching_child_obj)
                        notification = MatchNotification.objects.create(user=report.reporter,
                            lost_child=child,
                            matching_child=matching_child_obj)
                        serialized_notification = MatchNotificationSerializer(notification).data
                        async_to_sync(self.channel_layer.group_send)(
                            f"{report.reporter_id}",
                            {
                                "type": "match_found",
                                "message": serialized_notification["id"],
                            },
                        )
                        #matched_reports.append(matching_child_obj)
        #             distances.append(distance)

        # # serialize the matched reports and return as JSON
        # if flag:
        #     serializer = FoundChildSerializer(matched_reports, many=True)
        # else:
        #     serializer = LostChildSerializer(matched_reports, many=True)

        # output_data = []
        # for i, data in enumerate(serializer.data):
        #     output_data.append({
        #         'Child': OrderedDict(data.items()),
        #         'distance': {'distance': distances[i]}
        #     })
        #matchingReports_obj.reports.add(**matched_reports)
        print(model_to_dict(matchingReports_obj))
        output_data = MatchingReportsSerializer(matchingReports_obj).data

        return Response(output_data)


class ReceivedChildList(APIView):
    def get(self, request):
        # Get all LostChild reports with status="received"
        # lost_reports = LostChild.objects.filter(status='received')
        # lost_serializer = LostChildSerializer(lost_reports, many=True)

        # Get all FoundChild reports with status="received"
        found_reports = FoundChild.objects.filter(status='received')
        found_serializer = ReceivedChildrenSerializer(found_reports, many=True)

        # Combine the results and return the response
        # data = [
        #     *lost_serializer.data,
        #     *found_serializer.data
        # ]
        return Response(found_serializer.data, status=status.HTTP_200_OK)


"""class ReportListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.filter(reporter=request.user)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            report = Report.objects.get(pk=pk)
            if report.reporter != self.request.user:
                raise PermissionDenied
            return report
        except Report.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        report = self.get_object(pk)
        serializer = ReportSerializer(report)
        return Response(serializer.data)

    def put(self, request, pk):
        report = self.get_object(pk)
        serializer = ReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        report = self.get_object(pk)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)"""


class ReportsByUser(generics.ListAPIView):
    permission_classes = (IsAuthenticatedCustom,)
    serializer_class = {
        'lost_reports': LostChildSerializer,
        'found_reports': FoundChildSerializer
    }

    def get_queryset(self):
        user = self.request.user
        queryset = {
            "lost_reports": LostChild.objects.filter(reporter=user),
            "found_reports": FoundChild.objects.filter(reporter=user),
        }
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serialized_data = {}
        for key in queryset:
            serializer = self.serializer_class[key](queryset[key], many=True)
            serialized_data[key] = serializer.data
        return Response(serialized_data)
    
