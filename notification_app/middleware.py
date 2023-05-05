from urllib.parse import parse_qs
from channels.db import database_sync_to_async

import jwt
from datetime import datetime
from login_app.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class TokenAuthentication:
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the query parameters.
    For example:

        ?token=401f7ac837da42b97f613d789819ff93537bee6a
    """

    def authenticate_credentials(self, key):
        try:
            decoded_data = jwt.decode(
                key, settings.SECRET_KEY, algorithms="HS256")
        except Exception:
            return None

        # check if token as exipired
        exp = decoded_data["exp"]

        #if datetime.now().timestamp() > exp:
        #    return "Token expired"
        try:
            user = User.objects.get(id=decoded_data["user_id"])
            print(user.first_name)
            return user
        except Exception:
            return None


@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    # postpone model import to avoid ImproperlyConfigured error before Django
    # setup is complete.
    from django.contrib.auth.models import AnonymousUser

    if "token" not in scope:
        raise ValueError(
            "Cannot find token in scope. You should wrap your consumer in "
            "TokenAuthMiddleware."
        )
    token = scope["token"]
    user = None
    try:
        auth = TokenAuthentication()
        user = auth.authenticate_credentials(token)
    except AuthenticationFailed:
        pass
    return user or AnonymousUser()


class TokenAuthMiddleware:
    """
    Custom middleware that takes a token from the query string and authenticates via
    Django Rest Framework authtoken.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        query_params = parse_qs(scope["query_string"].decode())
        token = query_params["token"][0]
        scope["token"] = token
        scope["user"] = await get_user(scope)
        return await self.app(scope, receive, send)
