# from rest_framework import generics, status
# from channels.layers import get_channel_layer
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, permission_classes
# from channels.db import database_sync_to_async
# from .consumers import NotificationConsumer
# from .models import Notification
# from login_app.models import User
# from .serializers import NotificationSerializer
# from findmychild.custom_methods import IsAuthenticatedCustom
# from django.shortcuts import get_object_or_404

# class NotificationCreateView(generics.CreateAPIView):
#     queryset = Notification.objects.all()
#     serializer_class = NotificationSerializer
#     permission_classes = (IsAuthenticatedCustom, )

#     def post(self, request, *args, **kwargs):
#         data={}
#         user = request.user
#         other_user_id = request.data['otherUserId']
#         other_user = User.objects.get(id = other_user_id)
#         if user.user_type == 'appUser':
#             appUser = user
#             orgUser = other_user
#         else:
#             appUser = other_user
#             orgUser = user
        
#         data["room_name"] = f"chat_{min(user.first_name, other_user.first_name)}_{max(user.first_name, other_user.first_name)}"
#         serializer = self.serializer_class(data = data)
#         if serializer.is_valid():
#             serializer.save(appUser = appUser, orgUser = orgUser)
#             print(serializer.errors)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


