from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipe.models import FavoriteRecipe, Ingredient, Recipe, ShoppingList, Tag
from user.models import Follow

from .filters import CustomIngredientsSearchFilter
from .pagination import CustomPageNumberPagination
from .permissions import AdminOrAuthor, AdminOrReadOnly
from .serializers import (AmountIngredient, CreateUpdateRecipeSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    @action(
        detail=False,
        methods=['get'],
        url_path='/subscriptions',
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowSerializer
    )
    def subscriptions(self, request):  
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_follower = user.follower.all()
        for follower in user_follower:
            author = follower.author.id
        queryset = User.objects.filter(
            pk__in=author
        )
        serializer = self.get_serializer(
            self.paginate_queryset(queryset), many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path='(?P<user_pk>[^/.])/subscribe/',
        serializer_class=FollowSerializer
    )
    def subscribe(self, request, user_pk=None):
        user = self.request.user
        author = get_object_or_404(User, pk=user_pk)
        if request.method == 'POST':
            if user == author:
                message = {'Нельзя подписаться на самого себя'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(
                author=author, user=user
            ).exists():
                message = {'Вы уже подписаны на этого автора'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(
                author=author, user=user
            ).exists():
                message = {'Вы не подписаны на этого автора'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(
                Follow, author=author, user=user
            )
            subscription.delete()
            return Response("Вы отписались", status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    """Для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AdminOrAuthor,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='(?P<recipe_pk>[^/.]+)/favorite',
    )
    def favorite(self, request, pk=None):
        """Добавляет/удаляет рецепт в Избранное."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(
                user=user, recipe=recipe
            ).exists():
                message = {'Рецепт уже есть в избранном'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not FavoriteRecipe.objects.filter(
                user=user, recipe=recipe
            ).exists():
                message = {'Рецептa нет в избранном'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            favorite = get_object_or_404(
                FavoriteRecipe, user=user, recipe=recipe)
            favorite.delete()
            return Response(
                    'Рецепт удалён из избранного',
                    status=status.HTTP_204_NO_CONTENT
                )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='(?P<recipe_pk>[^/.]+)/shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет/удаляет рецепт в Списке покупок."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                message = {'Рецепт уже в списке покупок'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not ShoppingList.objects.filter(
                user=user, recipe=recipe
            ).exists():
                message = {'Рецептa нет в списке покупок'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)

            shopping_list = get_object_or_404(
                ShoppingList, user=user, recipe=recipe
            )
            shopping_list.delete()
            return Response(
                    'Рецепт удалён из списка покупок',
                    status=status.HTTP_204_NO_CONTENT
            )

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = AmountIngredient.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measurement_unit=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.first_name}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для:\n\n{user.first_name}\n\n'
        )
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient["ingredient"]}:'
                f'{ingredient["amount"]}'
                f'{ingredient["measurement_unit"]}'
            )
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class TagViewSet(ReadOnlyModelViewSet):
    """Для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    http_method_names = ['get']


class IngredientViewSet(ReadOnlyModelViewSet):
    """Для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = (CustomIngredientsSearchFilter,)
    search_fields = ('^name', 'name')
    http_method_names = ['get']
