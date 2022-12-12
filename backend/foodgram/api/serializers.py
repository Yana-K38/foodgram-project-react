from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipe.models import (AmountIngredient, FavoriteRecipe, Ingredient,
                           Recipe, ShoppingList, Tag)
from user.models import Follow

User = get_user_model()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор, укороченный список полей из модели Recipe."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = '__all__',


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
        )


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name',)

    def get_serializer_class(self):
        return ShortRecipeSerializer

    def get_recipes(self, obj):
        author = Recipe.objects.filter(author=obj)
        if 'recipes_limit' in self.context.get('request').GET:
            recipes_limit = self.context.get('request').GET['recipes_limit']
            author = author[:int(recipes_limit)]

        if author:
            serializer = self.get_serializer_class()(
                author,
                context={'request': self.context.get('request')},
                many=True
            )
            return serializer.data

        return []

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
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
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe_am__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj).exists()


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """Создание и редактирование рецепта."""
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(min_value=0)
        )
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(validators=(MinValueValidator(1),))

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe_am__amount'))
        return ingredients

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        all_ingredients = []
        for ingredient in ingredients:
            all_ingredients.append(AmountIngredient(
                recipe=recipe,
                ingredients=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount']
            ))
        AmountIngredient.objects.bulk_create(all_ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients:
            recipe.ingredients.clear()
            all_ingredients = [
                AmountIngredient(
                    recipe=recipe,
                    ingredients=get_object_or_404(
                        Ingredient, id=ingredient['id']
                    )
                )
                for ingredient in ingredients
            ]
            AmountIngredient.objects.bulk_create(all_ingredients)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        data = RecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}
        ).data
        return data
