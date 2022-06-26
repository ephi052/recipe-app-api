"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer  # set the serializer class to the UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer  # set the serializer class to the AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # set the renderer classes to the default renderer classes


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer  # set the serializer class to the UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)  # set the authentication classes to the
    # TokenAuthentication class
    permission_classes = (permissions.IsAuthenticated,)  # set the permission classes to the IsAuthenticated class

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user  # return the authenticated user from the request
