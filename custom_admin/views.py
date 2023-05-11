from django.shortcuts import render
from rest_framework import viewsets
from findmychild.custom_methods import IsAuthenticatedAdmin
from lostchildren.models import LostChild, FoundChild, MatchingReports
from lostchildren.serializers import LostChildSerializer, FoundChildSerializer, MatchingReportsSerializer
from login_app.models import User, OrgDetails, Location
from login_app.serializers import UserSerializer, LocationSerializer, OrgDetailsSerializer

# Create your views here.
class LostChildList(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticatedAdmin,)

    queryset = LostChild.objects.all()
    serializer_class = LostChildSerializer


class FoundChildList(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticatedAdmin,)

    queryset = FoundChild.objects.all()
    serializer_class = FoundChildSerializer

class AppUserList(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticatedAdmin,)

    queryset = User.objects.all()
    serializer_class = UserSerializer

class MatchingReportsList(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticatedAdmin,)

    queryset = MatchingReports.objects.all()
    serializer_class = MatchingReportsSerializer


