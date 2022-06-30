"""
serializers for rest api
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for recipe
    """
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'time_minutes', 'price', 'link')
        read_only_fields = ['id']