from django.urls import path
from django.conf import settings
from .views import RegisterUserView, LoginView, LogoutView, ChangePasswordView, ListLoggedInUser
from django.conf.urls.static import static

urlpatterns = [
    path('login_app/register', RegisterUserView.as_view(), name='register_user'),
    path('login_app/login', LoginView.as_view(), name='login_view'),
    path('login_app/logout-view', LogoutView.as_view(), name='logout_view'),
    path('login_app/change-password-view', ChangePasswordView.as_view(), name='change_password'),
    path('login_app/profile/', ListLoggedInUser.as_view(), name='logged_in_user_data'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)