from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from .views import LostChildList, FoundChildList, LostMatchedReports, ReceivedChildList, ReportsByUser, UpdateChildStatus, LostChildCreate, GetMatchedReports, image_view

router = routers.DefaultRouter()
router.register(r'lost-children', LostChildList)
router.register(r'found-children', FoundChildList)

urlpatterns = [
    path('', include(router.urls)),
    path('matched-reports/', LostMatchedReports.as_view(), name='matched_reports'),
    path('matching-reports/', GetMatchedReports.as_view(), name='matching_reports'),
    path('user-reports/', ReportsByUser.as_view(), name="user_reports"),
    path('create-lost-report/', LostChildCreate.as_view(),
         name="create_lost_child"),
    path('received-children/', ReceivedChildList.as_view(),
         name='received_child_view'),
    path('change-status/', UpdateChildStatus.as_view(),
         name='update_child_status_view'),
    path('image/found/<uuid:child_id>/', image_view,
         {'child_model': 'found'}, name='found_child_image_view'),
    path('image/lost/<uuid:child_id>/', image_view,
         {'child_model': 'lost'}, name='lost_child_image_view'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
