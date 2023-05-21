import json
import numpy as np
from collections import OrderedDict
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from findmychild.custom_methods import IsAuthenticatedCustom
from rest_framework.response import Response
from .models import LostChild, FoundChild, MatchingReports, MatchingChild
from .serializers import LostChildSerializer, FoundChildSerializer, ReceivedChildrenSerializer, MatchingChildSerializer, MatchingReportsSerializer
from .face_recognizer import feature_extractor, match_results
from django.forms.models import model_to_dict
from login_app.models import User, OrgDetails
from notification_app.models import MatchNotification, DropChildNotification
from notification_app.serializers import MatchNotificationSerializer, DropChildNotificationSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class LostChildren(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticatedCustom, )

    queryset = LostChild.objects.all()
    serializer_class = LostChildSerializer


class FoundChildren(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticatedCustom, )

    queryset = FoundChild.objects.all()
    serializer_class = FoundChildSerializer


class LostChildCreate(generics.CreateAPIView):
    # permission_classes = (IsAuthenticatedCustom, )
    serializer_class = LostChildSerializer

    def post(self, request, format=None):
        reportData = request.data
        # reportData["reporter"] = request.user.id
        serializer = self.serializer_class(data=reportData)
        serializer.is_valid(raise_exception=True)
        child = serializer.save()
        print(child)
        try:
            # queryset = FoundChild.objects.all()
            queryset = FoundChild.objects.filter(status='received')
            try:
                matchingReports_obj = child.matchingReports
            except Exception:
                matchingReports_obj = MatchingReports.objects.create(
                    lost_child=child)

        except FoundChild.DoesNotExist:
            return Response({'error': 'No Received Reports Found to Match with'}, status=404)
        # get image encoding of the child
        image_encoding = np.array(json.loads(child.image_encoding))

        # iterate through all reports and check for matching faces

        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None
            print(report.child_name)
            if child.gender == report.gender:
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
                    try:
                        matchingReports_obj.reports.get(
                            recieved_child_id=report.id)
                    except Exception:
                        match_obj = {
                            "recieved_child": model_to_dict(report),
                            "distance": distance
                        }
                        serialized_report = MatchingChildSerializer(
                            data=match_obj)
                        serialized_report.is_valid(raise_exception=True)
                        if serialized_report.is_valid(raise_exception=True):
                            matching_child_obj = serialized_report.save(
                                recieved_child=report)
                            matchingReports_obj.reports.add(matching_child_obj)

        # print(model_to_dict(matchingReports_obj))
        output_data = MatchingReportsSerializer(matchingReports_obj).data
        return Response(output_data)


class UpdateChildStatus(generics.UpdateAPIView):
    serializer_class = FoundChildSerializer
    channel_layer = get_channel_layer()
    permission_classes = (IsAuthenticatedCustom, )

    def patch(self, request, format=None):
        # get id of the FoundChild or LostChild object
        report_id = request.data.get('report_id', None)

        if not report_id:
            return Response({'error': 'Object report_id not found'}, status=400)
        found_report = FoundChild.objects.get(id=report_id)
        orgUser = User.objects.get(id=request.user.id)
        founder = found_report.reporter
        found_report.reporter = orgUser
        found_report.status = 'received'
        found_report.save()
        child = found_report
        try:
            queryset = LostChild.objects.all()
        except LostChild.DoesNotExist:
            return Response({'error': 'No Lost Reports Found to Match with'}, status=404)
        # get image encoding of the child
        image_encoding = np.array(json.loads(child.image_encoding))

        # iterate through all reports and check for matching faces
        matched_reports = []
        distances = []
        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None
            print(report.child_name)
            if child.gender == report.gender:
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
                    matched_reports.append(report)
                    distances.append(distance)
                    match_obj = {
                        "recieved_child": model_to_dict(child),
                        "distance": distance
                    }
                    serialized_report = MatchingChildSerializer(data=match_obj)
                    if serialized_report.is_valid(raise_exception=True):
                        matching_child_obj = serialized_report.save(
                            recieved_child=child)
                        try:
                            report.matchingReports.reports.add(
                                matching_child_obj)

                            notification = MatchNotification.objects.create(user_id=report.reporter.id,
                                                                            lost_child=report,
                                                                            matching_child_id=matching_child_obj.id, descript="Match Report")

                            serialized_notification = MatchNotificationSerializer(
                                notification).data
                            print(serialized_notification)
                            async_to_sync(self.channel_layer.group_send)(
                                f"{report.reporter_id}",
                                {
                                    "type": "match_found",
                                    "message": serialized_notification,
                                },
                            )
                        except Exception:
                            print(Exception)
        try:
            drop_notification = DropChildNotification.objects.create(type= "drop_child_success", description="Child is Received Successfully",user = founder, found_child = child  )
            serialized_drop_notification = DropChildNotificationSerializer(drop_notification).data
            async_to_sync(self.channel_layer.group_send)(
                                f"{founder.id}",
                                {
                                    "type": "drop_child_success",
                                    "message": serialized_drop_notification,
                                },
                            )
        except Exception as e:
            return Exception(e)
        serializer = LostChildSerializer(matched_reports, many=True)

        output_data = []
        for i, data in enumerate(serializer.data):
            output_data.append({
                'Child': OrderedDict(data.items()),
                'distance': {'distance': distances[i]}
            })

        return Response(output_data)


class LostMatchedReports(APIView):
    channel_layer = get_channel_layer()

    def post(self, request, format=None):
        # get id of the FoundChild or LostChild object
        id = request.data.get('id', None)
        if not id:
            return Response({'error': 'Object id not found'}, status=400)

        try:
            child = LostChild.objects.get(id=id)
            # queryset = FoundChild.objects.all()
            queryset = FoundChild.objects.filter(status='received')
            try:
                matchingReports_obj = child.matchingReports
            except Exception:
                matchingReports_obj = MatchingReports.objects.create(
                    lost_child=child)

        except FoundChild.DoesNotExist:
            return Response({'error': 'No Received Reports Found to Match with'}, status=404)
        # get image encoding of the child
        image_encoding = np.array(json.loads(child.image_encoding))

        # iterate through all reports and check for matching faces

        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None
            print(report.child_name)
            if child.gender == report.gender:
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
                    try:
                        matchingReports_obj.reports.get(
                            recieved_child_id=report.id)
                    except Exception:
                        match_obj = {
                            "recieved_child": model_to_dict(report),
                            "distance": distance
                        }
                        serialized_report = MatchingChildSerializer(
                            data=match_obj)
                        serialized_report.is_valid(raise_exception=True)
                        if serialized_report.is_valid(raise_exception=True):
                            matching_child_obj = serialized_report.save(
                                recieved_child=report)
                            matchingReports_obj.reports.add(matching_child_obj)

        # print(model_to_dict(matchingReports_obj))
        output_data = MatchingReportsSerializer(matchingReports_obj).data
        return Response(output_data)


class GetMatchedReports(APIView):
    permission_classes = (IsAuthenticatedCustom, )
    serializer_class = MatchingReportsSerializer

    def post(self, request):
        lost_child = LostChild.objects.get(id=request.data["id"])
        matched_reports = MatchingReports.objects.get(lost_child=lost_child)
        serialized_obj = self.serializer_class(matched_reports)

        return Response(serialized_obj.data, status=status.HTTP_200_OK)


class ReceivedChildList(APIView):
    permission_classes = (IsAuthenticatedCustom, )

    def get(self, request):

        # Get all FoundChild reports with status="received"
        found_reports = FoundChild.objects.filter(status='received')
        found_serializer = ReceivedChildrenSerializer(found_reports, many=True)

        return Response(found_serializer.data, status=status.HTTP_200_OK)
    
class FoundChildList(APIView):
    permission_classes = (IsAuthenticatedCustom, )

    def get(self, request):

        # Get all FoundChild reports with status="received"
        found_reports = FoundChild.objects.filter(status='received')
        found_serializer = ReceivedChildrenSerializer(found_reports, many=True)

        return Response(found_serializer.data, status=status.HTTP_200_OK)


def image_view(request, child_id, child_model):
    child_model_map = {
        'found': FoundChild,
        'lost': LostChild,
    }

    ChildModel = child_model_map.get(child_model)

    if not ChildModel:
        return HttpResponse('Invalid child model.')

    child = get_object_or_404(ChildModel, id=child_id)

    if child.image:
        with open(child.image.path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/jpeg')

    return HttpResponse('Image not found.')


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
