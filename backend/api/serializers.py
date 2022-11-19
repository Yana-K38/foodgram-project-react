from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F

from recipe.models import AmountIngredient, Ingredient, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
   # author = 
    tags = TagSerializer(many=True, read_only=True)
    ingredient = IngredientSerializer(many=True, read_only=True)
   # is_favorited = serializers.SerializerMethodField()
   # is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = '__all__'



    # def update(self, recipe, validated_data):
    #     tags = validated_data.get('tags')
    #     ingredients = validated_data.get('ingredients')
    #     recipe.name = validated_data.get('name', recipe.name)
    #     recipe.text = validated_data.get('text', recipe.text)
    #     recipe.cooking_time = validated_data.get(
    #         'cooking_time', recipe.cooking_time
    #         )
    #     recipe.image = validated_data.get('image', recipe.image)

    #     if ingredients:
    #         recipe.ingredients.clear()
    #         lst = []
    #         for ingredient in ingredients:
    #             current_ingredient, created = AmountIngredient.objects.get_or_create(
    #                     ingredients=Ingredient.objects.get(id=ingredient.get('id')),
    #                     amount=ingredient['amount']
    #                     )
    #             lst.append(current_ingredient)
    #         recipe.ingredients.set(lst)

    #     if tags:
    #         recipe.tags.clear()
    #         recipe.tags.set('tags')

    #     recipe.save()
    #     return recipe
