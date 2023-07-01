from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from .views import AnalyticsData, AppUserUserListView, AgencyUserListView, LostChildList

# router = routers.DefaultRouter()
# router.register(r'lost-children', LostChildList)
# router.register(r'found-children', FoundChildList)

urlpatterns = [
    # path('', include(router.urls)),
    path('analytics', AnalyticsData.as_view(), name='analytics'),
    path('all-app-users', AppUserUserListView.as_view(), name='all_app_user_data'),
    path('all-agency-users', AgencyUserListView.as_view(), name='all_agencies_data'),
    path('lost-children', LostChildList.as_view(), name= "lost_children")
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
