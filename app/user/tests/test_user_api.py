"""
Test for the User API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


class publicUserApiTests(TestCase):
    """Test the public features of user API"""

    def setUp(self):
        self.client = APIClient()  # create a new client object to make requests to the API

    def test_create_user_success(self):
        """Test creating user is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)  # post request to create user endpoint with payload and
        # return response object

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # 201 created status code is returned when user is
        # created successfully in the API endpoint
        user = get_user_model().objects.get(email=payload['email'])  # get user from db with the email that was created
        self.assertTrue(user.check_password(payload['password']))  # check if password is correct
        self.assertNotIn('password', res.data)  # check if password is not in the response data

    def test_user_email_exists_error(self):
        """Test creating a user with an existing email fails"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        create_user(**payload)  # create user with the email in the payload
        res = self.client.post(CREATE_USER_URL, payload)  # post request to create user endpoint

        self.assertEqual(res.status_code,
                         status.HTTP_400_BAD_REQUEST)  # 400 bad request status code is returned when user email
        # already exists in the API endpoint

    def test_password_too_short_error(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)  # post request to create user endpoint

        self.assertEqual(res.status_code,
                         status.HTTP_400_BAD_REQUEST)  # 400 bad request status code is returned when password is too
        # short
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()  # check if user with the email in the payload exists in the db
        self.assertFalse(user_exists)  # check if user does not exist in the db

    def test_create_token_for_user(self):
        """Test generating token for valid credentials"""
        user_details = {
            'name': 'Test name',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**user_details)  # create user with the details in the user_details dict

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL,
                               payload)  # post request to create token endpoint with payload and return response object
        self.assertIn('token', res.data)  # check if token is in the response data
        self.assertEqual(res.status_code,
                         status.HTTP_200_OK)  # 200 ok status code is returned when token is created successfully in
        # the API endpoint

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@example.com', password='goodpass')  # create user

        payload = {
            'email': 'test@example.com',
            'passwoard': 'badpass',
        }
        res = self.client.post(TOKEN_URL, payload)  # post request to create token

        self.assertNotIn('token', res.data)  # check if token is not in the response data
        self.assertEqual(res.status_code,
                         status.HTTP_400_BAD_REQUEST)  # 400 bad request status code is returned when token is not
        # created successfully in the API endpoint

    def test_create_token_blank_password(self):
        """Test that token is not created if password is blank"""
        create_user(email='test@example.com', password='goodpass')  # create user

        payload = {
            'email': 'test@example.com',
            'passwoard': '',
        }
        res = self.client.post(TOKEN_URL, payload)  # post request to create token

        self.assertNotIn('token', res.data)  # check if token is not in the response data
        self.assertEqual(res.status_code,
                         status.HTTP_400_BAD_REQUEST)  # 400 bad request status code is returned when token is not
        # created successfully in the API endpoint

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)  # get request to retrieve user endpoint

        self.assertEqual(res.status_code,
                         status.HTTP_401_UNAUTHORIZED)  # 401 unauthorized status code is returned when user is not
        # authenticated in the API endpoint


class PrivetUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test name'
        )
        self.client = APIClient()  # create a new client object to make requests to the API
        self.client.force_authenticate(
            user=self.user)  # force authenticate user with the user object (force becose we want to test other
        # parmiters than the othentication)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)  # get request to retrieve user endpoint

        self.assertEqual(res.status_code,
                         status.HTTP_200_OK)  # 200 ok status code is returned when user is retrieved successfully in
        # the API endpoint
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })  # check if user details are in the response data

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})  # post request to retrieve user endpoint

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)  # 405 method not allowed status code

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            'name': 'new name',
            'password': 'newpassword123'
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # refresh user from db

        self.assertEqual(self.user.name, payload['name'])  # check if user name is updated
        self.assertTrue(self.user.check_password(payload['password']))  # check if password is updated
        self.assertEqual(res.status_code,
                         status.HTTP_200_OK)  # 200 ok status code is returned when user is updated successfully in
        # the API endpoint
