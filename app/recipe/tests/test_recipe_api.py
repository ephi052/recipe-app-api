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