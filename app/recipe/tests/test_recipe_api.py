"""
Tests for recipe APIs.
"""
from decimal import Decimal
import email
from unicodedata import decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='email@example.com,', password='password123')

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='password123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test retrieving a recipe detail."""
        recipe = create_recipe(user=self.user)

        res = self.client.get(detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Test recipe',
            'price': Decimal('5.99'),
            'time_minutes': 30,
            'description': 'This is a test recipe.',
            'link': 'http://example.com/recipe.pdf',
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED) # 201 created new resource created
        recipe = Recipe.objects.get(id=res.data['id']) # get the recipe from db
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)  # Check that user is set

        def test_partial_update_recipe(self):
            """Test updating a recipe with patch."""
            original_link = 'http://example.com/recipe.pdf'
            recipe = create_recipe(
                user=self.user,
                title='Pizza',
                link=original_link,
                )
            payload = {'title': 'Chicken'}
            url = detail_url(recipe.id)
            res = self.client.patch(url, payload)

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            recipe.refresh_from_db()
            self.assertEqual(recipe.title, payload['title'])
            self.assertEqual(recipe.link, original_link)
            self.assertEqual(recipe.user, self.user)

        def test_full_update_recipe(self):
            """Test full update of a recipe with put."""
            recipe = create_recipe(
                user=self.user,
                title='Pizza',
                link='http://example.com/recipe.pdf',
                description='This is a test recipe.',
                )
            payload = {
                'title': 'Chicken',
                'link': 'http://example.com/chicken.pdf',
                'description': 'This is a naw test recipe.',
                'time_minutes': 30,
                'price': Decimal('5.99'),
            }
            url = detail_url(recipe.id)
            res = self.client.put(url, payload)

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            recipe.refresh_from_db()
            for k, v in payload.items():
                self.assertEqual(getattr(recipe, k), v)
            self.assertEqual(recipe.user, self.user)

        def test_user_update_returns_error(self):
            """Test that only authenticated user can update a recipe."""
            new_user = create_user(email='examp@example.com', password='password123')
            recipe = create_recipe(user=self.user)

            payload = {'user': new_user.id}
            url = detail_url(recipe.id)
            self.client.pach(url, payload)

            recipe.refresh_from_db()
            self.assertEqual(recipe.user, self.user)

        def test_delete_recipe(self):
            """Test deleting a recipe."""
            recipe = create_recipe(user=self.user)
            url = detail_url(recipe.id)
            res = self.client.delete(url)

            self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
            self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

        def test_recipe_other_user_recipe_error(self):
            """Test that only authenticated user can delete a recipe."""
            new_user = create_user(email='ouser@example.com', password='password123')
            recipe = create_recipe(user=new_user)

            url = detail_url(recipe.id)
            res = self.client.delete(url)

            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
            self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())