from django.http import HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, UpdateAPIView
from .models import User, Jwt, AgencyProfile, AppUserProfile, Role
from notification_app.models import OrgVerifyNotification
from notification_app.serializers import OrgVerifyNotificationSerializer
from django.dispatch import receiver
from .authentication import Authentication
from findmychild.custom_methods import IsAuthenticatedCustom, IsAuthenticatedAdmin
from django.forms.models import model_to_dict
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    RefreshSerializer,
    SimpleOrgUserSerializer,
    AgencyProfileSerializer,
    AppUserProfileSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from django.forms.models import model_to_dict
from rest_framework.response import Response
from django_rest_passwordreset.signals import reset_password_token_created
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.core.mail import EmailMessage
import random
import string
import jwt
from django.db.models import Q, Count, OuterRef
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from .email import send_otp_via_email
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import FileResponse
import threading
from lostchildren.signals import delete_child_image
# Create your views here.


def get_random(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def get_access_token(payload):
    return jwt.encode(
        {"exp": datetime.now() + timedelta(minutes=15), **payload},
        settings.SECRET_KEY,
        algorithm="HS256"
    )


def get_refresh_token():
    return jwt.encode(
        {"exp": datetime.now() + timedelta(days=365), "data": get_random(10)},
        settings.SECRET_KEY,
        algorithm="HS256"
    )


def decodeJWT(bearer):
    if not bearer:
        return None

    token = bearer[7:]
    decoded = jwt.decode(token, key=settings.SECRET_KEY, algorithms=["HS256"])
    if decoded:
        try:
            return User.objects.get(id=decoded["user_id"])
        except Exception:
            return None


def sendSignUpNotificaiton(user):
    channel_layer = get_channel_layer()
    admin = User.objects.filter(is_staff=True).first()
    notification = OrgVerifyNotification.objects.create(
        type="verification_request", user_id=admin.id, description="Verification Request", org_user=user)
    serialized_notification = OrgVerifyNotificationSerializer(
        notification).data
    print(serialized_notification)
    async_to_sync(channel_layer.group_send)(
        "admin_group",
        {
            "type": "verification_request",
            "message": serialized_notification,
        },
    )


class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    code = None

    def post(self, request):
        user_serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if user_serializer.validate_email(request.data["email"]):
            print(request.data)
            email = request.data['email']
            first_name = request.data['first_name']
            if (request.data['last_name']):
                last_name = request.data['last_name']
            phone_no = request.data['phone_no']
            # Generate a random 4-digit code and store it in the user's session
            self.code = random.randint(1000, 9999)
            print("code", self.code)
            request.session['registration_code'] = self.code
            send_otp_via_email(email, self.code)
            request.session['registration_email'] = email
            request.session['registration_first_name'] = first_name
            if (last_name):
                request.session['registration_last_name'] = last_name
            request.session['registration_phone_no'] = phone_no
            return Response({"message": "success"})
        else:
            return Response({"message": "Invalid email address"})

    def patch(self, request):
        self.code = request.session.get('registration_code')
        print("in patch", self.code)
        if self.code is None:
            request.session['code_status'] = False
            return Response({"message": "No registration in progress"})

        # Verify that the code provided by the user matches the code in the session
        code_received = request.data.pop('code')
        print("received code", code_received)
        if not code_received or str(code_received) != str(self.code):
            request.session['code_status'] = False
            return Response({"message": "Invalid code"})
        request.session['code_status'] = True
        return Response({"message": "success"})

    def put(self, request):
        data = {}
        # Check if the user has a registration code in their session
        code = request.session.get('code_status')
        if not code:
            return Response({"message": "No registration in progress"})

        data = request.data.copy()
        data['email'] = request.session.get('registration_email')
        data['first_name'] = request.session.get('registration_first_name')
        data['last_name'] = request.session.get('registration_last_name')
        data['phone_no'] = request.session.get('registration_phone_no')
        print(data)
        # Create the user account
        user_serializer = self.serializer_class(
            data=data, context={'request': request})
        if user_serializer.is_valid():
            user = user_serializer.save()
            if user.role == Role.AGENCY:
                print("Agency User Yesssss")
                AgencyProfile.objects.create(user=user)
                thread = threading.Thread(
                    target=sendSignUpNotificaiton, args=(user,))
                thread.start()
                # sendSignUpNotificaiton(user)
            request.session.flush()
            return Response({"message": "User registered successfully"})
        else:
            print(user_serializer.errors)
            return Response({"message": "Invalid password"})


class ForgotPassword(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data
        try:
            email = data.get('email')
            user = User.objects.get(email=email)
            code = random.randint(1000, 9999)
            request.session['email'] = email
            request.session['registration_code'] = code
            send_otp_via_email(email, code)
            return Response({"message": "success"})
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Email is not registered!")

    def patch(self, request, *args, **kwargs):
        code = request.session.get('registration_code')
        if code is None:
            request.session['code_status'] = False
            print({"message": "No registration in progress"})
            return Response({"message": "No registration in progress"})

        received_code = request.data.get('code')
        if not received_code or str(received_code) != str(code):
            request.session['code_status'] = False
            print({"message": "Invalid code"})
            return Response({"message": "Invalid code"})

        request.session['code_status'] = True
        return Response({"message": "success"})

    def put(self, request):
        code_status = request.session.get('code_status')
        if not code_status:
            return Response({"message": "No registration in progress"})

        email = request.session.get('email')
        user = User.objects.get(email=email)
        user.set_password(request.data.get("password"))
        user.save()
        return Response({"message": "Password changed successfully"})


class LoginView(APIView):

    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email=data["email"])
            # token = Token.objects.get_or_create(user=user)
            if user.check_password(data["password"]):
                Jwt.objects.filter(user_id=user.id).delete()
                access = get_access_token({"user_id": str(user.id)})
                refresh = get_refresh_token()
                data = dict()
                data["message"] = "User logged in succesfully"
                data["user"] = UserSerializer(user).data
                data["status"] = "success"
                data["token"] = access
                data["refresh"] = refresh

                Jwt.objects.create(
                    user_id=user.id, access=access, refresh=refresh
                )
                response = Response(data)
                response.set_cookie('refresh_token', refresh, httponly=True,
                                    expires=datetime.now() + timedelta(days=30))
                return response
            return Exception("Password did not Matched")
        except Exception as e:
            return Exception("Error Signing In")


class LogoutView(APIView):
    permission_classes = (IsAuthenticatedCustom, )

    def get(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"message": "successfully logged out"})


class ChangePasswordView(APIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def post(self, request):
        user = request.user
        if user:
            # check password method validates the password, we can not validate password without check method because it is hashed
            if user.check_password(request.data["old_password"]):
                print("match")
                user.set_password(request.data["new_password"])
                user.save()
                return Response({"message": "Password Changed successfully"})
            else:
                return Response({"message": "Previous Password incorrect"})


"""
    USER PROFILES
"""


class ListLoggedInAppUser(RetrieveAPIView):
    serializer_class = AppUserProfileSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def get(self, request):
        try:
            # print (reset_password_token.user.email)
            try:
                app_user = AppUserProfile.objects.get(user=request.user)
            except:
                app_user = AppUserProfile.objects.create(user=request.user)
            if app_user:
                response = self.serializer_class(app_user).data
                print(response)
            return Response(response)
        except Exception as e:
            return print(e)


class ListLoggedInAgencyUser(RetrieveAPIView):
    serializer_class = AgencyProfileSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def get(self, request):
        try:
            # print (reset_password_token.user.email)
            try:
                org_user = AgencyProfile.objects.get(user=request.user)
            except:
                org_user = AgencyProfile.objects.create(user=request.user)
            if org_user:
                response = self.serializer_class(org_user).data
                print(response)
            return Response(response)
        except Exception as e:
            return print(e)


"""
    UPDATE USER
"""


def user_profile_photo_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    file_path = user.profile_photo.path
    return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')


class UpdateLoggedInUser(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # parser_classes = [MultiPartParser, FormParser]
    permission_classes = (IsAuthenticatedCustom, )

    def patch(self, request, *args, **kwargs):
        user_instance = request.user
        old_profile_picture = user_instance.profile_photo
        # print(request.data)
        user_serializer = self.get_serializer(
            user_instance, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        if (request.data.get("profile_photo")):
            delete_child_image(old_profile_picture.path)
        if user.role == Role.AGENCY:
            # Assuming a one-to-one relationship between User and Profile
            profile_instance = user.agency
            profile_serializer = AgencyProfileSerializer(
                profile_instance, data=request.data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
            print(user_serializer.data)
            return Response(user_serializer.data)

        # Assuming a one-to-one relationship between User and Profile
        profile_instance = user.appUser
        profile_serializer = AppUserProfileSerializer(
            profile_instance, data=request.data, partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        return Response(user_serializer.data)

# class UpdateLoggedInUser(RetrieveAPIView):
#     serializer_class = UserSerializer
#     permission_classes = (IsAuthenticatedCustom, )

#     def patch(self, request):
#         try:
#             # print (reset_password_token.user.email)
#             logged_user = User.objects.get(email=request.user.email)
#             updated_user = request.data
#             if logged_user:
#                 for key, value in updated_user.items():
#                     setattr(logged_user, key, value)
#                 logged_user.save()
#                 response = self.serializer_class(
#                     logged_user, context={"request": request}).data
#             return Response(response)
#         except Exception as e:
#             return Response(e)


# class UpdateLoggedInOrgUser(RetrieveAPIView):
#     serializer_class = OrgDetailsSerializer
#     permission_classes = (IsAuthenticatedCustom, )

#     def patch(self, request):
#         try:
#             # print (reset_password_token.user.email)
#             org_user = OrgDetails.objects.get(user=request.user)
#             updated_user = request.data
#             for key, value in updated_user.items():
#                 setattr(org_user, key, value)
#                 setattr(org_user.user, key, value)
#                 org_user.save()
#                 response = self.serializer_class(
#                     org_user, context={"request": request}).data
#             return Response(response)
#         except Exception as e:
#             return Response(e)


# class ListAllOrgUser(ListAPIView):
#     serializer_class = OrgDetailsSerializer
#     permission_classes = (IsAuthenticatedCustom, )

#     def get_queryset(self):
#         users = User.objects.filter(role=Role.AGENCY)
#         queryset = OrgDetails.objects.filter(user__in=users)
#         return queryset

#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = self.get_queryset()
#             print(queryset)
#             if queryset:
#                 response = self.serializer_class(queryset, many=True).data
#             return Response(response)
#         except Exception as e:
#             return Response(e)

class AppUserUserListView(ListAPIView):
    queryset = AppUserProfile.objects.filter(user__role=Role.APPUSER.value)
    serializer_class = AppUserProfileSerializer


class AgencyUserListView(ListAPIView):
    queryset = AgencyProfile.objects.filter(user__role=Role.AGENCY.value)
    serializer_class = AgencyProfileSerializer


class UnverifiedOrgs(ListAPIView):

    permission_classes = (IsAuthenticatedCustom, )
    serializer_class = SimpleOrgUserSerializer

    def get_queryset(self):
        return User.objects.filter(role=Role.AGENCY, is_active=False)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            response = self.serializer_class(queryset, many=True).data
            return Response(response)
        except Exception as e:
            return Response(e)


class VerifyOrgUser(APIView):
    permission_classes = (IsAuthenticatedAdmin,)
    serializer_class = UserSerializer
    channel_layer = get_channel_layer()

    def post(self, request, *args, **kwargs):
        try:
            agencyId = request.data["id"]
            agency = User.objects.get(id=agencyId)
            print(agency)
            agency.is_active = True
            agency.save()
            serialized_user = self.serializer_class(agency).data
            async_to_sync(self.channel_layer.group_send)(
                f"{agency.id}",
                {
                    "type": "verification_success",
                    "message": serialized_user,
                },
            )
            return Response({"message": "Org is successfuly verified"})
        except User.DoesNotExist:
            return Response({"message": "User not found"})
        except Exception as e:
            return Response({"message": str(e)})


class RefreshView(APIView):
    serializer_class = RefreshSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            active_jwt = Jwt.objects.get(
                refresh=serializer.validated_data["refresh"])
        except Jwt.DoesNotExist:
            return Response({"error": "refresh token not found"}, status="400")
        if not Authentication.verify_token(serializer.validated_data["refresh"]):
            return Response({"error": "Token is invalid or has expired"})

        access = get_access_token({"user_id": active_jwt.user.id})
        refresh = get_refresh_token()

        active_jwt.access = access.decode()
        active_jwt.refresh = refresh.decode()
        active_jwt.save()

        return Response({"access": access, "refresh": refresh})


# this signal is fired when we post request at "api/password_rest" it returns a token
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    user_email = reset_password_token.user.email
    url = "http://127.0.0.1:8000/api/password_reset/confirm/" + \
        "?token=" + reset_password_token.key
    email = EmailMessage('Password change request', url, to=[
                         reset_password_token.user.email])
    email.send()
