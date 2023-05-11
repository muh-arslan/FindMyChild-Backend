from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from .views import LostChildList, FoundChildList, MatchedReports, ReceivedChildList, LostChildCreate, ReportsByUser, image_view

router = routers.DefaultRouter()
router.register(r'lost-children', LostChildList)
router.register(r'found-children', FoundChildList)

urlpatterns = [
    path('', include(router.urls)),
    path('matched-reports/', MatchedReports.as_view(), name='matched_reports'),
    path('lost-reports/create', LostChildCreate.as_view(), name='lost_report_create'),
    path('user-reports/', ReportsByUser.as_view(), name="user_reports"),
    path('received-children/', ReceivedChildList.as_view(),
         name='received_child_view'),
    path('image/<uuid:child_id>/', image_view, name='image_view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)