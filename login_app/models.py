from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group
from django.utils import timezone
from uuid import uuid4


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


def user_profile_photo_path(instance, filename):
    return f'pictures/{instance.id}/{filename}'


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    AGENCY = "AGENCY", "Agency"
    APPUSER = "APPUSER", "AppUser"


class User(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    role = models.CharField(max_length=50, choices=Role.choices)
    username = None
    email = models.EmailField(_('email address'), unique=True)
    is_online = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    # Field to associate user with groups
    groups = models.ManyToManyField(Group, blank=True)
    online_status = models.BooleanField(default=False, null=True, blank=True)
    profile_photo = models.ImageField(
        blank=True, upload_to=user_profile_photo_path)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.email


class AppUserProfile(models.Model):
    provinces_choices = [('AJK', 'Azad Jammu and Kashmir'),    ('Bal', 'Balochistan'),    (
        'GB', 'Gilgit Baltistan'),    ('KP', 'Khyber Pakhtunkhwa'),    ('Pun', 'Punjab'),    ('Snd', 'Sindh')]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(
        User, related_name='appUser', on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    phone_no = models.CharField(max_length=20, null=True, blank=True)
    province = models.CharField(
        max_length=18, choices=provinces_choices, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name = 'AppUser'
        verbose_name_plural = 'AppUsers'


class AgencyProfile(models.Model):

    provinces_choices = [('AJK', 'Azad Jammu and Kashmir'),    ('Bal', 'Balochistan'),    (
        'GB', 'Gilgit Baltistan'),    ('KP', 'Khyber Pakhtunkhwa'),    ('Pun', 'Punjab'),    ('Snd', 'Sindh')]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(
        User, related_name='agency', on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    phone_no = models.CharField(max_length=20, null=True, blank=True)
    province = models.CharField(
        max_length=18, choices=provinces_choices, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    slogan = models.TextField(blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=32, decimal_places=15, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=32, decimal_places=15, blank=True, null=True)

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name = 'Agency'
        verbose_name_plural = 'Agencies'


# class Favorite(models.Model):
#     user = models.OneToOneField(User, related_name="user_favorites", on_delete=models.CASCADE)
#     favorite = models.ManyToManyField(User, related_name="user_favoured")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username}"

#     class Meta:
#         ordering = ("created_at",)


class Jwt(models.Model):
    user = models.OneToOneField(
        User, related_name="login_user", on_delete=models.CASCADE)
    access = models.TextField()
    refresh = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
