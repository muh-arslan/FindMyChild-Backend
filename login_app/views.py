from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from rest_framework.views import APIView
from django.views.generic import ListView, DetailView, View
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView, ListCreateAPIView
from .models import User
from django.dispatch import receiver
from rest_framework.reverse import reverse
from .serializers import ( 
                          UserSerializer, 
                          LoginSerializer,
                          ChangePasswordSerializer,
                          RequestChangePasswordSerializer
                        )
from rest_framework.response import Response
from django_rest_passwordreset.signals import reset_password_token_created
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate,login,logout
from django.core.mail import EmailMessage
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
import random
# Create your views here.
    
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
            #email = user_serializer.validated_data['email']
            email = request.data['email']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            phone_no = request.data['phone_no']
            # Generate a random 5-digit code and store it in the user's session
            code = random.randint(10000, 99999)
            request.session['registration_code'] = code
            request.session['registration_email'] = email
            request.session['registration_first_name'] = first_name
            request.session['registration_last_name'] = last_name
            request.session['registration_phone_no'] = phone_no
            # Send the code to the user's email address
            # send_mail(
            #     'Registration Code',
            #     f'Your registration code is: {code}',
            #     'noreply@example.com',
            #     [email],
            #     fail_silently=False,
            # )
            return Response({"message": "A 5-digit code has been sent to your email address", "code": code})
        else:
            return Response({"message": "Invalid email address"})

    def put(self, request):
        data = {}
        # Check if the user has a registration code in their session
        code = request.session.get('registration_code')
        if not code:
            return Response({"message": "No registration in progress"})
        
        data = request.data.copy()
        data['email'] = request.session.get('registration_email')
        data['first_name'] = request.session.get('registration_first_name')
        data['last_name'] = request.session.get('registration_last_name')
        #data['phone_no'] = request.session.get('registration_phone_no') 
        # Verify that the code provided by the user matches the code in the session
        code_received = request.data.get('code')
        if not code_received or str(code_received) != str(code):
            return Response({"message": "Invalid code"})
        
        # Create the user account
        user_serializer = self.serializer_class(data=data, context={'request': request})
        print(user_serializer.is_valid())
        if user_serializer.is_valid():
            user = user_serializer.save()
            request.session.flush()
            return Response({"message": "User registered successfully"})
        else:
            return Response({"message": "Invalid password"})
            
    
class LoginView(APIView):

    serializer_class = LoginSerializer
    
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email=data["email"])
            token = Token.objects.get_or_create(user=user)
            print(token[0].key)
            response = dict()
            response["user_id"] = user.id
            response["status"] = "success"
            response["token"] = token[0].key
            return Response(response)
        except Exception as e:
            print(e)
        
class LogoutView(APIView):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"message": "successfully logged out"})
        

class ChangePasswordView(APIView):
    
    serializer_class = ChangePasswordSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            # print (reset_password_token.user.email)
            logged_user = User.objects.get(email=request.user.email)
            if logged_user:
                response = self.serializer_class(logged_user, context={"request": request}).data
            return Response(response)
        except Exception as e:
            return Response(e)
        

# this signal is fired when we post request at "api/password_rest" it returns a token
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    user_email = reset_password_token.user.email
    url = "http://127.0.0.1:8000/api/password_reset/confirm/" + "?token=" + reset_password_token.key
    email = EmailMessage('Password change request', url, to=[reset_password_token.user.email])
    email.send()