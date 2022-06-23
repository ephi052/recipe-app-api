"""
Test for the User API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


class publicUserApiTests(TestCase):
    """Test the public features of user API"""
    def setUp(self):
        self.client = APIClient() # create a new client object to make requests to the API

    def test_create_user_success(self):
        """Test creating user is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload) # post request to create user endpoint with payload and return response object

        self.assertEqual(res.status_code, status.HTTP_201_CREATED) # 201 created status code is returned when user is created successfully in the API endpoint
        user = get_user_model().objects.get(email=payload['email']) # get user from db with the email that was created
        self.assertTrue(user.check_password(payload['password'])) # check if password is correct
        self.assertNotIn('password', res.data) # check if password is not in the response data

    def test_user_email_exists_error(self):
        """Test creating a user with an existing email fails"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        create_user(**payload) # create user with the email in the payload
        res = self.client.post(CREATE_USER_URL, payload) # post request to create user endpoint

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST) # 400 bad request status code is returned when user email already exists in the API endpoint

    def test_password_too_short_error(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload) # post request to create user endpoint

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST) # 400 bad request status code is returned when password is too short
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists() # check if user with the email in the payload exists in the db
        self.assertFalse(user_exists) # check if user does not exist in the db
