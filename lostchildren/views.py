from django.shortcuts import render
from .models import LostChild, FoundChild
from rest_framework import viewsets
from .serializers import LostChildSerializer, FoundChildSerializer


class LostChildList(viewsets.ModelViewSet):
    queryset = LostChild.objects.all()
    serializer_class = LostChildSerializer


class LostChildDetail(viewsets.ModelViewSet):
    queryset = LostChild.objects.all()
    serializer_class = LostChildSerializer


class FoundChildList(viewsets.ModelViewSet):
    queryset = FoundChild.objects.all()
    serializer_class = FoundChildSerializer


class FoundChildDetail(viewsets.ModelViewSet):
    queryset = FoundChild.objects.all()
    serializer_class = FoundChildSerializer
