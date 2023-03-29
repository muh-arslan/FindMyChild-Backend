from django.urls import path, include
from rest_framework import routers
from .views import LostChildList, LostChildDetail

router = routers.DefaultRouter()
router.register(r'lost-children', LostChildList)
router.register(r'lost-children/<int:pk>', LostChildDetail)

urlpatterns = [
    path('', include(router.urls)),
]
