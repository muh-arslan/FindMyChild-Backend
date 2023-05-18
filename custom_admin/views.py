from django.shortcuts import render
from rest_framework import viewsets, generics
from findmychild.custom_methods import IsAuthenticatedAdmin
from lostchildren.models import LostChild, FoundChild, MatchingReports
from lostchildren.serializers import LostChildSerializer, FoundChildSerializer, MatchingReportsSerializer
from login_app.models import User, OrgDetails
from login_app.serializers import UserSerializer, OrgDetailsSerializer
from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse

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

class GraphData(generics.ListAPIView):

    permission_classes = (IsAuthenticatedAdmin,)

    def get_stats(self):

        current_year = timezone.now().year

        # Calculate the count of Org users joined for each month of the current year
        org_users_joined_count = User.objects.filter(created_at__year=current_year, user_type="orgUser").annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Calculate the count of App users joined for each month of the current year
        app_users_joined_count = User.objects.filter(created_at__year=current_year, user_type="appUser").annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Calculate the count of lost reports created for each month of the current year
        lost_reports_created_count = LostChild.objects.filter(created_at__year=current_year).annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Calculate the count of found reports created for each month of the current year
        found_reports_created_count = FoundChild.objects.filter(created_at__year=current_year, status="found").annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Calculate the count of received reports created for each month of the current year
        received_reports_created_count = LostChild.objects.filter(created_at__year=current_year, status="received").annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        return {
            'org_users_joined_count': org_users_joined_count,
            'app_users_joined_count': app_users_joined_count,
            'lost_reports_created_count': lost_reports_created_count,
            'found_reports_created_count': found_reports_created_count,
            'received_reports_created_count': received_reports_created_count,
        }
    
    def list(self, request, *args, **kwargs):
        stats = self.get_stats()
        return JsonResponse(stats)
    
class AnalyticsData(generics.ListAPIView):

    permission_classes = (IsAuthenticatedAdmin,)

    def get_stats(self):

        current_year = timezone.now().year

        # Calculate the count of Org users 
        org_users_count = User.objects.filter( user_type="orgUser").count()
        # Calculate the count of App users 
        app_users_count = User.objects.filter( user_type="appUser").count()

        # Calculate the count of lost reports 
        lost_reports_count = LostChild.objects.count()
        # Calculate the count of found reports 
        found_reports_count = FoundChild.objects.count()

        # Calculate the count of received reports 
        received_reports_count = LostChild.objects.count()

        # Calculate the count of Org users joined for each month of the current year
        org_users_joined_count = User.objects.filter(created_at__year=current_year, user_type="orgUser").annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Calculate the count of App users joined for each month of the current year
        app_users_joined_count = User.objects.filter(created_at__year=current_year, user_type="appUser").annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # # Calculate the count of lost reports created for each month of the current year
        # lost_reports_created_count = LostChild.objects.filter(created_at__year=current_year).annotate(
        #     month=ExtractMonth('created_at')
        # ).values('month').annotate(count=Count('id')).order_by('month')

        # # Calculate the count of found reports created for each month of the current year
        # found_reports_created_count = FoundChild.objects.filter(created_at__year=current_year, status="found").annotate(
        #     month=ExtractMonth('created_at')
        # ).values('month').annotate(count=Count('id')).order_by('month')

        # # Calculate the count of received reports created for each month of the current year
        # received_reports_created_count = LostChild.objects.filter(created_at__year=current_year, status="received").annotate(
        #     month=ExtractMonth('created_at')
        # ).values('month').annotate(count=Count('id')).order_by('month')
        return {
            'org_users_count': org_users_count,
            'app_users_count': app_users_count,
            'lost_reports_count': lost_reports_count,
            'found_reports_count': found_reports_count,
            'received_reports_count': received_reports_count,

            'org_users_joined_count': list(org_users_joined_count),
            'app_users_joined_count': list(app_users_joined_count),
            # 'lost_reports_created_count': lost_reports_created_count,
            # 'found_reports_created_count': found_reports_created_count,
            # 'received_reports_created_count': received_reports_created_count,
        }
    
    def list(self, request, *args, **kwargs):
        stats = self.get_stats()
        print(stats)
        return JsonResponse(stats,safe=False)


    
    


