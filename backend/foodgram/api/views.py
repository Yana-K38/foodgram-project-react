from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipe.models import FavoriteRecipe, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from user.models import Follow

from .filters import CustomIngredientsSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import AdminOrAuthor, AdminOrReadOnly
from .serializers import (AmountIngredient, CreateUpdateRecipeSerializer,
                          FavoriteSerializator, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPageNumberPagination
    serializer_class = UserSerializer

    @action(
        detail=False,
        # methods=['get'],
        permission_classes=[IsAuthenticated]
        # url_path="subscriptions",
    )
    # def subscriptions(self, request):
    #     user = request.user
    #     queryset = User.objects.filter(following__user=user)
    #     pages = self.paginate_queryset(queryset)
    #     serializer = FollowSerializer(
    #         pages, many=True, context={'request': request}
    #     )
    #     return self.get_paginated_response(serializer.data)
    def subscriptions(self, request):
        user = self.request.user
        user_subscription = user.follower.all()
        author = [follower.author.id for follower in user_subscription]
        queryset = User.objects.filter(pk__in=author).order_by('id')
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            paginated_queryset, many=True, context={'request': request}
        )
        # serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    # def subscribe(self, request, id):
    #     user = request.user
    #     author = get_object_or_404(User, pk=id)
    #     if request.method == 'POST':
    #         serializer = FollowSerializer(
    #             author, data=request.data, context={'request': request}
    #         )
    #         serializer.is_valid(raise_exception=True)
    #         Follow.objects.create(user=user, author=author)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     if request.method == 'DELETE':
    #         get_object_or_404(
    #             Follow, user=user, author=author
    #         ).delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    def subscribe(self, request, pk=None):
        user = self.request.user
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            if user == author:
                message = {'Нельзя подписаться на самого себя'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(
                author=author, user=user
            ).exists():
                message = {'Вы уже подписаны на этого автора'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(
                author=author,
                user=user
            ).exists():
                message = {'Вы не подписаны на этого автора'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(
                Follow, author=author, user=user
            )
            subscription.delete()
            return Response(
                "Вы отписались", status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(ModelViewSet):
    """Для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AdminOrAuthor, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавляет/удаляет рецепт в Избранное."""
        context = {'request': request}
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(
                user=user, recipe=recipe
            ).exists():
                message = {'Рецепт уже есть в избранном'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            data = {
                'user': request.user.id,
                'recipe': recipe.id
            }
            serializer = FavoriteSerializator(
                data=data, context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
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
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет/удаляет рецепт в Списке покупок."""
        context = {'request': request}
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                message = {'Рецепт уже в списке покупок'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            data = {
                'user': request.user.id,
                'recipe': recipe.id
            }
            serializer = ShoppingCartSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
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
        methods=['get']
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
                f' {position_ingredient.name.title()},'
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
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None
    http_method_names = ['get']


class IngredientViewSet(ReadOnlyModelViewSet):
    """Для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None
    filter_backends = (CustomIngredientsSearchFilter, )
    search_fields = ('^name', 'name')
    http_method_names = ['get']
