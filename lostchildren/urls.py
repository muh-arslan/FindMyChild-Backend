from django.urls import path, include
from rest_framework import routers
from .views import LostChildList, FoundChildList, MatchedReports, ReceivedChildList

router = routers.DefaultRouter()
router.register(r'lost-children', LostChildList)
router.register(r'found-children', FoundChildList)

urlpatterns = [
    path('', include(router.urls)),
    path('matched-reports/', MatchedReports.as_view(), name='matched_reports'),
    path('received-children/', ReceivedChildList.as_view(),
         name='received_child_view'),
]
