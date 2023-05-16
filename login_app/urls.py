from django.urls import path, include
from django.conf import settings
from .views import RegisterUserView, LoginView, LogoutView, ChangePasswordView, ListLoggedInUser, RefreshView, ListLoggedInOrgUser, ListAllOrgUser, ForgotPassword
from django.conf.urls.static import static

urlpatterns = [
    path('refresh', RefreshView.as_view()),
    path('register', RegisterUserView.as_view(), name='register_user'),
    path('login', LoginView.as_view(), name='login_view'),
    path('forgot-password', ForgotPassword.as_view(), name='forgot-password'),
    path('logout-view', LogoutView.as_view(), name='logout_view'),
    path('change-password-view', ChangePasswordView.as_view(),
         name='change_password'),
    path('profile', ListLoggedInUser.as_view(), name='logged_in_user_data'),
    path('org-profile', ListLoggedInOrgUser.as_view(),
         name='logged_in_org_user_data'),
    path('all-orgs', ListAllOrgUser.as_view(), name='all_org_user_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
