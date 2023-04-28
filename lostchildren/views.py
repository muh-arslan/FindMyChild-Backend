import json
import numpy as np
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import LostChild, FoundChild
from .serializers import LostChildSerializer, FoundChildSerializer
from .face_recognizer import feature_extractor, match_results


class LostChildList(viewsets.ModelViewSet):
    queryset = LostChild.objects.all()
    serializer_class = LostChildSerializer


class FoundChildList(viewsets.ModelViewSet):
    queryset = FoundChild.objects.all()
    serializer_class = FoundChildSerializer


class MatchedReports(APIView):

    def post(self, request, format=None):
        # extract image from the request
        image = request.data.get('image', None)
        if not image:
            return Response({'error': 'Image not found'}, status=400)

        # extract encodings of the uploaded image
        image_encoding = feature_extractor(image)

        # get all lost or found reports depending on the type of the uploaded report
        flag = True
        if request.data.get('type') == 'lost':
            queryset = FoundChild.objects.all()
        else:
            flag = False
            queryset = LostChild.objects.all()

        # iterate through all reports and check for matching faces
        matched_reports = []
        for report in queryset:
            if report.image_encoding is not None:
                report_encoding = np.array(json.loads(report.image_encoding))
            else:
                report_encoding = None
            print(type(report_encoding), type(image_encoding))
            if report_encoding is not None and np.all(match_results(image_encoding, report_encoding)):
                matched_reports.append(report)

        # serialize the matched reports and return as JSON
        if flag:
            serializer = FoundChildSerializer(matched_reports, many=True)
        else:
            serializer = LostChildSerializer(matched_reports, many=True)

        return Response(serializer.data)


class ReceivedChildList(APIView):
    def get(self, request):
        # Get all LostChild reports with status="received"
        lost_reports = LostChild.objects.filter(status='received')
        lost_serializer = LostChildSerializer(lost_reports, many=True)

        # Get all FoundChild reports with status="received"
        found_reports = FoundChild.objects.filter(status='received')
        found_serializer = FoundChildSerializer(found_reports, many=True)

        # Combine the results and return the response
        data = [
            *lost_serializer.data,
            *found_serializer.data
        ]
        return Response(data, status=status.HTTP_200_OK)


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
