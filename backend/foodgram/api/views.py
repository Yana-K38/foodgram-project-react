from datetime import datetime as dt
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
from rest_framework.pagination import PageNumberPagination

from recipe.models import FavoriteRecipe, Ingredient, Recipe, ShoppingList, Tag
from user.models import Follow

from .filters import CustomIngredientsSearchFilter
from .pagination import CustomPageNumberPagination
from .permissions import AdminOrAuthor, AdminOrReadOnly
from .serializers import (AmountIngredient, CreateUpdateRecipeSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer, ShortRecipeSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination
    serializer_class=FollowSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
       pass
        # current_user = request.user
        # queryset = get_object_or_404(Follow, user=current_user)
        # queryset = self.filter_queryset(queryset)
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = self.get_serializer(queryset, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)

        # user = self.request.user
        # if user.is_anonymous:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)
        # user_follower = user.follower.all()
        # for follower in user_follower:
        #     author = follower.author.id
        # queryset = User.objects.filter(
        #     pk__in=author
        # )
        # serializer = self.get_serializer(
        #     self.paginate_queryset(queryset), many=True
        # )
        # return self.get_paginated_response(serializer.data)

        # queryset = self.get_queryset().filter(
        #     following__user=request.user
        # ).order_by('pk')
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = FollowSerializer(
        #         page, many=True, context={'request': request}
        #     )
        #     return self.get_paginated_response(serializer.data)
        # serializer = FollowSerializer(
        #     queryset, many=True, context={'request': request}
        # )
        # return Response(serializer.data, status=status.HTTP_200_OK)
        

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path="(?P<user_pk>[^/.])/subscribe",
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
            serializer = ShortRecipeSerializer(
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
            serializer = ShortRecipeSerializer(
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
        shopping_list = AmountIngredient.objects.filter(
            recipe__in_shopping_list__user=request.user
        ).values('ingredients').annotate(
            amount=Sum('amount')
        )
        shopping_cart_file = (
            f'Список покупок для: {user.username}\n'
            f'{dt.now().strftime("%d/%m/%Y")}\n\n'
        )
        for ingredient in shopping_list:
            position_ingredient = get_object_or_404(
                Ingredient,
                pk=ingredient['ingredients']
            )
            position_amount = ingredient['amount']
            shopping_cart_file += (
                f' {position_ingredient.name.title()}'
                f' {position_ingredient.measurement_unit}'
                f' - {position_amount}' + '\n'
            )
        response = HttpResponse(
            shopping_cart_file,
            content_type='text'
        )
        response['Content-Disposition'] = (
            'attachment; filename="%s"' % 'shopping_list.txt'
        )
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
