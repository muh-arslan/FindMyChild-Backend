from LoginApp.models import User
from django.http import response
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
# Create your tests here.
print("intests")

# first of all make a class like following to test all your apis
class LoginApiTests(APITestCase):
    # run the command dump data to make db.json file and put it in fixtures
    fixtures = ['demo.json', ]
    
    # this function is responsible for logging in the user and authenticating it
    def _login_user(self):
        print("in login")
        self.user = User.objects.get(email='1@1.com')
        print(Token.objects.all())
        self.client.login(email="1@1.com", password="1")
        # self.client.force_authenticate(user=self.user)
        print("this is self.user" , self.user)

    # 'setUp' is just like a construction in your test class it is sure to execute
    def setUp(self):
        print("in set up")
        self._login_user()
        
    # the name of your api testing function must start with word 'test' otherwise it wont work
    def test_get_profile(self):
        # client = APIClient()
        # client.credentials(HTTP_AUTHORIZATION='Token 66736302d0142bd7af0b05c933157a5e4610e42b')
        # response = self.client.get(reverse('logged_in_user_data'), headers= {'Authorization':'Token 66736302d0142bd7af0b05c933157a5e4610e42b'})
        # response = self.client.get(reverse('logged_in_user_data'), HTTP_AUTHORIZATION='Token 66736302d0142bd7af0b05c933157a5e4610e42b')
        response = self.client.get(reverse('logged_in_user_data'))
        print(response)
        self.assertEqual(response.data.get('email'), "1@1.com")
        
        
    def test_register_user(self):
        data_post = {
                    "first_name": "string",
                    "last_name": "string",
                    "email": "user@example.com",
                    "password": "string",
                    "confirmPassword": "string",
                    "profile_photo": "string"
                    }
        response = self.client.post(reverse('register_user'), data_post, format='json')
        print(response)
        
    def test_change_password(self):
        data_post = {
                    "old_password": "string",
                    "new_password": "string"
                    }
        response = self.client.post(reverse('change_password'), data_post, format='json')
        print(response)