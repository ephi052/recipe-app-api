"""
test for recipe api
"""
from decimal import Decimal
from email.policy import default

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


def create_recipe(**params):
    """
    Create a recipe instance in the database
    """
    defaults = {
        'title': 'Test recipe',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'A test recipe',
        'link': 'http://test.com',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

RECIPE_URL = reverse('recipe:recipe-list')

class PublicRecipeApiTests(TestCase):
    """
    Test unauthenticated recipe API access
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required
        """
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class privateRecipeApiTests(TestCase):
    """
    Test authenticated recipe API access
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """
        Test retrieving a list of recipes
        """
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """
        Test list recipes is limites to othenticated user
        """
        other_user = get_user_model().objects.create_user(
            'user2@example.com',
            'testpass'
        )  # create a second user
        create_recipe(user=other_user)  # create a recipe for other user
        create_recipe(user=self.user)  # create a recipe for current user

        res = self.client.get(RECIPE_URL)  # get all recipes for user 1

        recipes = Recipe.objects.filter(user=self.user)  # get all recipes for user 1
        serializer = RecipeSerializer(recipes, many=True)  # serialize the recipes
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # check status code
        self.assertEqual(len(res.data), 1)  # check that only one recipe is returned
        self.assertEqual(res.data, serializer.data)  # check that the data is correct


