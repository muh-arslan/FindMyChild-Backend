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
# Create your views here.
    
class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    
    def post(self, request):
        response = dict()
        user_serializer = self.serializer_class(data=request.data, context={'request': request})
        if user_serializer.is_valid():
            user = user_serializer.save()
            response["email"] = user.email
            response["message"] = "User registered successfully"
            return Response(response)
        else:
            return Response({"message": "invalid values entered"})
            
    
class LoginView(APIView):

    serializer_class = LoginSerializer
    
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email=data["email"])
            token = Token.objects.get_or_create(user=user)
            print(token[0].key)
            print(request.user)
            response = dict()
            response["message"] = "User logged in succesfully"
            response["token"] = token[0].key
            return Response(response)
        except Exception as e:
            print(e)
        
class LogoutView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"message": "successfully logged out"})
        

class ChangePasswordView(APIView):
    
    serializer_class = ChangePasswordSerializer
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

        
        
        
    
        
    
    
    