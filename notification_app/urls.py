# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    # #path("", views.index, name="index"),
    path("user-notifications", views.ListUserNotificationsView.as_view(),
         name="get_user_notifications"),
    path('contact-us/', views.ContactUsView.as_view(), name='contact-us'),
    path('feedback-review/', views.FeedbackReviewView.as_view(),
         name='feedback-review'),
]
