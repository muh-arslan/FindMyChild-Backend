import json
import numpy as np
from collections import OrderedDict
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import LostChild, FoundChild
from .serializers import LostChildSerializer, FoundChildSerializer, ReceivedChildrenSerializer
from .face_recognizer import feature_extractor, match_results


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


class MatchedReports(APIView):

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
            except FoundChild.DoesNotExist:
                return Response({'error': 'Object not found'}, status=404)

        if request.data.get('type') == 'found':
            flag = False
            try:
                child = FoundChild.objects.get(id=id)
                queryset = LostChild.objects.all()
            except LostChild.DoesNotExist:
                return Response({'error': 'Object not found'}, status=404)

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

            if child.gender == report.gender:
                print(report.child_name)
                is_matched, distance = match_results(
                    image_encoding, report_encoding)
                if report_encoding is not None and np.all(is_matched):
                    matched_reports.append(report)
                    distances.append(distance)

        # serialize the matched reports and return as JSON
        if flag:
            serializer = FoundChildSerializer(matched_reports, many=True)
        else:
            serializer = LostChildSerializer(matched_reports, many=True)

        output_data = []
        for i, data in enumerate(serializer.data):
            output_data.append({
                'Child': OrderedDict(data.items()),
                'distance': {'distance': distances[i]}
            })

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


class LostReportsList(generics.ListCreateAPIView):
    serializer_class = LostChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return LostChild.objects.filter(reporter=user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class LostReportsDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LostChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return LostChild.objects.filter(reporter=user)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs["pk"])
        return obj


class FoundReportsList(generics.ListCreateAPIView):
    serializer_class = FoundChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FoundChild.objects.filter(reporter=user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class FoundReportsDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FoundChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FoundChild.objects.filter(reporter=user)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs["pk"])
        return obj
