from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,RetrieveAPIView, ListAPIView
from .models import User, Jwt, OrgDetails
from django.dispatch import receiver
from rest_framework.reverse import reverse
from .authentication import Authentication
from findmychild.custom_methods import IsAuthenticatedCustom
from django.forms.models import model_to_dict
from .serializers import ( 
                          UserSerializer, 
                          LoginSerializer,
                          ChangePasswordSerializer,
                          RequestChangePasswordSerializer,
                          RefreshSerializer,
                          OrgDetailsSerializer
                        )
from rest_framework.response import Response
from django_rest_passwordreset.signals import reset_password_token_created
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from django.contrib.auth import authenticate,login,logout
from django.core.mail import EmailMessage
from rest_framework.authtoken.models import Token
import random
import string
import jwt
import re
from django.db.models import Q, Count, OuterRef
from datetime import datetime, timedelta
# Create your views here.

def get_random(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def get_access_token(payload):
    return jwt.encode(
        {"exp": datetime.now() + timedelta(minutes=5), **payload},
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


class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    
    # def post(self, request):
    #     response = dict()
    #     user_serializer = self.serializer_class(data=request.data, context={'request': request})
    #     if user_serializer.is_valid():
    #         user = user_serializer.save()
    #         response["email"] = user.email
    #         response["message"] = "User registered successfully"
    #         return Response(response)
    #     else:
    #         return Response({"message": "invalid values entered"})

    def post(self, request):
        user_serializer = self.serializer_class(data=request.data, context={'request': request})
        if user_serializer.validate_email(request.data["email"]):
            print(request.data)
            #email = user_serializer.validated_data['email']
            email = request.data['email']
            first_name = request.data['first_name']
            if(request.data['last_name']):
                last_name = request.data['last_name']
            phone_no = request.data['phone_no']
            # Generate a random 5-digit code and store it in the user's session
            code = random.randint(1000, 9999)
            request.session['registration_code'] = code
            request.session['registration_email'] = email
            request.session['registration_first_name'] = first_name
            if(last_name):
                request.session['registration_last_name'] = last_name
            request.session['registration_phone_no'] = phone_no
            return Response({"message": "success", "code": code})
        else:
            return Response({"message": "Invalid email address"})
    
    def patch(self, request):
        code = request.session.get('registration_code')
        if not code:
            request.session['code_status'] = False
            return Response({"message": "No registration in progress"})
            
        # Verify that the code provided by the user matches the code in the session
        code_received = request.data.pop('code')
        if not code_received or str(code_received) != str(code):
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
        user_serializer = self.serializer_class(data=data, context={'request': request})
        if user_serializer.is_valid():
            user_serializer.save()
            print(user_serializer.data)
            request.session.flush()
            return Response({"message": "User registered successfully"})
        else:
            print(user_serializer.errors)
            return Response({"message": "Invalid password"})
            
    
class LoginView(APIView):

    serializer_class = LoginSerializer
    
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email=data["email"])
            #token = Token.objects.get_or_create(user=user)
            if user.check_password(data["password"]):
                Jwt.objects.filter(user_id=user.id).delete()
                access = get_access_token({"user_id": str(user.id)})
                refresh = get_refresh_token()
                response = dict()
                response["message"] = "User logged in succesfully"
                response["user"] = UserSerializer(user).data
                response["status"] = "success"
                response["token"] = access
                response["refresh"] = refresh

                Jwt.objects.create(
                    user_id=user.id, access=access, refresh=refresh
                )
                print(response)
                return Response(response)
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
            
                

        
class ListLoggedInUser(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedCustom, )
    def get(self, request):
        try:
            # print (reset_password_token.user.email)
            logged_user = User.objects.get(email=request.user.email)
            if logged_user:
                response = self.serializer_class(logged_user, context={"request": request}).data
            return Response(response)
        except Exception as e:
            return Response(e)
        
class ListLoggedInOrgUser(RetrieveAPIView):
    serializer_class = OrgDetailsSerializer
    permission_classes = (IsAuthenticatedCustom, )
    def get(self, request):
        try:
            # print (reset_password_token.user.email)
            org_user = OrgDetails.objects.get(user=request.user)
            print( model_to_dict(org_user))
            if org_user:
                response = self.serializer_class(org_user).data
                print(response)
            return Response(response)
        except Exception as e:
            return Response(e)
        
class ListAllOrgUser(ListAPIView):
    serializer_class = OrgDetailsSerializer
    permission_classes = (IsAuthenticatedCustom, )
    
    def get_queryset(self):
        users = User.objects.filter(user_type="orgUser")
        queryset = OrgDetails.objects.filter(user__in=users)
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            print(queryset)
            if queryset:
                response = self.serializer_class(queryset, many=True).data
            return Response(response)
        except Exception as e:
            return Response(e)



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
    url = "http://127.0.0.1:8000/api/password_reset/confirm/" + "?token=" + reset_password_token.key
    email = EmailMessage('Password change request', url, to=[reset_password_token.user.email])
    email.send()