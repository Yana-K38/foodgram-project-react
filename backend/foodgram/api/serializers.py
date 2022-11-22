from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F

from recipe.models import AmountIngredient, Ingredient, Recipe, Tag
from user.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""
    class Meta:
        model = User
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',

class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
   # author = 
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe_am__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        return bool(
            self.context.get('request').query_params.get('is_favorited')
        )

    def get_is_in_shopping_cart(self, obj):
        return bool(
            self.context.get('request').query_params.get('is_in_shopping_cart')
        )

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
            )
        recipe.image = validated_data.get('image', recipe.image)

        if ingredients:
            recipe.ingredients.clear()
            lst = []
            for ingredient in ingredients:
                current_ingredient, created = AmountIngredient.objects.get_or_create(
                        ingredients=Ingredient.objects.get(id=ingredient.get('id')),
                        amount=ingredient['amount']
                        )
                lst.append(current_ingredient)
            recipe.ingredients.set(lst)

        if tags:
            recipe.tags.clear()
            recipe.tags.set('tags')

        recipe.save()
        return recipe