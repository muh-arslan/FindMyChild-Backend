from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from .views import AnalyticsData

# router = routers.DefaultRouter()
# router.register(r'lost-children', LostChildList)
# router.register(r'found-children', FoundChildList)

urlpatterns = [
    # path('', include(router.urls)),
    path('analytics', AnalyticsData.as_view(), name='analytics'),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
