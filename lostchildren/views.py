from django.shortcuts import render
from .models import LostChild
from rest_framework import viewsets
from .serializers import LostChildSerializer


class LostChildList(viewsets.ModelViewSet):
    queryset = LostChild.objects.all()
    serializer_class = LostChildSerializer


class LostChildDetail(viewsets.ModelViewSet):
    queryset = LostChild.objects.all()
    serializer_class = LostChildSerializer
