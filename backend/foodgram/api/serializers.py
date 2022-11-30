from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F

from recipe.models import AmountIngredient, Ingredient, Recipe, Tag
from user.models import UserProfile, Follow
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()

class UserProfileSerializer(UserCreateSerializer, UserSerializer):
    """Сериализатор для пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        """Проверяет подписки пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return Follow.objects.filter(user=user, following=obj.id).exists()
    
    def create(self, validated_data):
        """ Создаёт нового пользователя."""

        user = UserProfile.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user




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
    author = UserProfileSerializer(read_only=True)
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
        return bool(
            self.context.get('request').query_params.get('is_favorited')
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.carts.filter(id=obj.id).exists()

    def create(self, validated_data):
        """
        """
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            AmountIngredient.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['ingredient'],
                amount=ingredient['amount']
            )
        for id in tags:
            recipe.tag.add(Tag.objects.get(id=id))

        return recipe
        
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

class UserFollowSerializer(UserProfileSerializer):
    """Сериализатор вывода авторов, на которых подписан текущий пользователь."""
    recipe = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


    class FollowSerializer(serializers.ModelSerializer):
        user = serializers.SlugRelatedField(
            slug_field='username', read_only=True,
            default=serializers.CurrentUserDefault()
        )
        following = serializers.SlugRelatedField(
            slug_field='username', queryset=User.objects.all())

        class Meta:
            fields = '__all__'
            model = Follow
            validators = [
                UniqueTogetherValidator(
                    queryset=Follow.objects.all(),
                    fields=('user', 'following'),
                    message='Вы уже подписаны на этого автора'
                )
            ]

        def validate(self, data):
            if self.context['request'].user == data['following']:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя!')
            return data