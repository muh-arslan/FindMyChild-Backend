from django.urls import path, include
from rest_framework import routers
from .views import LostChildList, LostChildDetail, FoundChildList, FoundChildDetail

router = routers.DefaultRouter()
router.register(r'lost-children', LostChildList)
router.register(r'lost-children/<int:pk>', LostChildDetail)
router.register(r'found-children/', FoundChildList)
router.register(r'found-children/<int:pk>', FoundChildDetail)

urlpatterns = [
    path('', include(router.urls)),
]
