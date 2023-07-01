from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.contrib.auth import authenticate
from login_app.models import User
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

class IsAuthenticatedCustom(BasePermission):

    def has_permission(self, request, view):
        from login_app.views import decodeJWT
        user = decodeJWT(request.META['HTTP_AUTHORIZATION'])
        if not user:
            return False
        request.user = user
        if request.user and request.user.is_authenticated:
            User.objects.filter(id=request.user.id).update(
                is_online=timezone.now())
            return True
        return False
    
class IsAuthenticatedAdmin(BasePermission):

    def has_permission(self, request, view):
        from login_app.views import decodeJWT
        user = decodeJWT(request.META['HTTP_AUTHORIZATION'])
        print("called")
        if not user:
            return False
        request.user = user
        if request.user and request.user.is_authenticated:
            if request.user.is_staff:
                User.objects.filter(id=request.user.id).update(
                    is_online=timezone.now())
                return True
        return False

class PermissionRequiredCustom(BasePermission):
    """Verify that the current user has all specified permissions."""
    permission_required = None

    def get_permission_required(self):
        """
        Override this method to override the permission_required attribute.
        Must return an iterable.
        """
        print(self.permission_required)
        if self.permission_required is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the "
                f"permission_required attribute. Define "
                f"{self.__class__.__name__}.permission_required, or override "
                f"{self.__class__.__name__}.get_permission_required()."
            )
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms

    def has_permission(self, request, *args, **kwargs):
        """
        Override this method to customize the way permissions are checked.
        """        
        from login_app.views import decodeJWT
        user = decodeJWT(request.META['HTTP_AUTHORIZATION'])
        print("called")
        if not user:
            raise PermissionDenied("Anonymous")
        request.user = user
        if request.user and request.user.is_authenticated:
            perms = self.get_permission_required()
            print(request.user)
            return request.user.has_perms(perms)
        raise PermissionDenied("Not authorized")

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            raise PermissionDenied("Denied")
        return super().dispatch(request, *args, **kwargs)

class IsAuthenticatedOrReadCustom(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user and request.user.is_authenticated:
            from login_app.models import User
            User.objects.filter(id=request.user.id).update(
                is_online=timezone.now())
            return True
        return False


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        return response

    exc_list = str(exc).split("DETAIL: ")

    return Response({"error": exc_list[-1]}, status=403)
