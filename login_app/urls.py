from django.urls import path, include
from django.conf import settings
from .views import ListLoggedInAgencyUser, ListLoggedInAppUser, RegisterUserView, LoginView, LogoutView, ChangePasswordView, AgencyUserListView, RefreshView, AppUserUserListView, ForgotPassword, UnverifiedOrgs, VerifyOrgUser, UpdateLoggedInUser, user_profile_photo_view
# ,UpdateLoggedInOrgUser
from django.conf.urls.static import static

urlpatterns = [
    path('refresh', RefreshView.as_view()),
    path('register', RegisterUserView.as_view(), name='register_user'),
    path('login', LoginView.as_view(), name='login_view'),
    path('forgot-password', ForgotPassword.as_view(), name='forgot-password'),
    path('logout-view', LogoutView.as_view(), name='logout_view'),
    path('change-password-view', ChangePasswordView.as_view(),
         name='change_password'),
    path('profile', ListLoggedInAppUser.as_view(), name='logged_in_user_data'),
    path('org-profile', ListLoggedInAgencyUser.as_view(),
         name='logged_in_org_user_data'),

    path('update-profile', UpdateLoggedInUser.as_view(),
         name='update_logged_in_user'),
#     path('update-org-profile', UpdateLoggedInOrgUser.as_view(),
#          name='update_logged_in_org_user'),

#     path('all-orgs', ListAllOrgUser.as_view(), name='all_org_user_data'),
    path('all-app-users', AppUserUserListView.as_view(), name='all_app_user_data'),
    path('all-agency-users', AgencyUserListView.as_view(), name='all_agency_user_data'),
    path('unverified-orgs', UnverifiedOrgs.as_view(), name='unverified_orgs'),
    path('verify-org-user', VerifyOrgUser.as_view(), name='verify_org_user'),
    path('user/profile-photo/<uuid:user_id>/',
         user_profile_photo_view, name='user_profile_photo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
