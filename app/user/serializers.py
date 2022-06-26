"""
Serializers for user API views.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()  # get the user model from the django contrib auth
        fields = ('email', 'password', 'name')  # only include the email, password and name fields in the serializer
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}  # set the min length of the password to 5

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)  # create a new user with the validated data

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)  # get the password from the validated data
        user = super().update(instance, validated_data)  # update the user with the validated data

        if password:  # if the password is not empty
            user.set_password(password)  # set the password
            user.save()  # save the user with the new password

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),  # get the request from the context
            username=email,  # get the email from the request
            password=password  # get the password from the request
        )  # authenticate the user
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')  # raise an error if the user cannot be
            # authenticated

        attrs['user'] = user  # add the user to the attrs dictionary
        return attrs  # return the attrs dictionary
