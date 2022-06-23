"""
Serializers for user API views.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model() # get the user model from the django contrib auth
        fields = ('email', 'password', 'name') # only include the email, password and name fields in the serializer
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}} # set the min length of the password to 5

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data) # create a new user with the validated data