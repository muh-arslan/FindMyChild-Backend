from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from .views import GetSingleChildView, DeleteChildView, LostChildList, FoundChildList, ReceivedChildCreate, ReportUpdateAPIView, LostMatchedReports, GetMatchedReports, ReceivedChildList, ReportsByUser, UpdateChildStatus, LostChildCreate, FoundChildCreate, SearchView, LostChildren, FoundChildren, image_view

# router = routers.DefaultRouter()
# router.register(r'lost-children', LostChildren)
# router.register(r'found-children', FoundChildren)

urlpatterns = [
    #     path('', include(router.urls)),
    path('matched-reports/', LostMatchedReports.as_view(), name='matched_reports'),
    path('matching-reports/', GetMatchedReports.as_view(), name='matching_reports'),
    path('user-reports/', ReportsByUser.as_view(), name="user_reports"),
    path('create-lost-report/', LostChildCreate.as_view(),
         name="create_lost_child"),
    path('create-received-report/', ReceivedChildCreate.as_view(),
         name='received_child_create_view'),
    path('create-found-report/', FoundChildCreate.as_view(),
         name='found_child_create_view'),
    path('lost-children/', LostChildList.as_view(), name='lost_child_view'),
    path('found-children/', FoundChildList.as_view(), name='found_child_view'),
    path('received-children/', ReceivedChildList.as_view(),
         name='received_child_view'),
    path('report-update/<uuid:pk>/', ReportUpdateAPIView.as_view(),
         name='child_update_view'),
    path('change-status/', UpdateChildStatus.as_view(),
         name='update_child_status_view'),
    path('image/child/<uuid:child_id>/',
         image_view, name='found_child_image_view'),
    path('report-delete/<uuid:pk>/',
         DeleteChildView.as_view(), name='delete_child'),
    path('search/<str:keyword>/', SearchView.as_view(), name='search_child'),
    path('child/<uuid:id>/', GetSingleChildView.as_view(), name="single_child_view" )

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
