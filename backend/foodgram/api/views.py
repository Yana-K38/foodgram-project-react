from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.pagination import PageNumberPagination
from recipe.models import Tag, Ingredient, Recipe
from user.models import UserProfile, Follow
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, UserProfileSerializer, AmountIngredient, UserFollowSerializer
from .permissions import AdminOrReadOnly, AuthorOrStaffOrReadOnly
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.http.response import HttpResponse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from django.db.models import F, Sum
from djoser.views import UserViewSet


class UserProfileViewSet(UserViewSet):
    """Для работы с пользователями."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (AuthorOrStaffOrReadOnly,)


class FollowViewSet(UserViewSet):
    pagination_class = PageNumberPagination

    @action(detail=False, permission_classes=(AuthorOrStaffOrReadOnly,))
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = UserFollowSerializer(page, many=True,
                                           context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post'],
            permission_classes=[AuthorOrStaffOrReadOnly,])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(UserProfile, id=id)
        if user == author:
            return Response({'errors':
                            _('Вы не можете подписаться на себя.')},
                            status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({'errors':
                            _('Вы уже подписались на автора.')},
                            status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=user, author=author)
        queryset = Follow.objects.get(user=request.user, author=author)
        serializer = UserFollowSerializer(queryset,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_del(self, request, id=None):
        user = request.user
        author = get_object_or_404(UserProfile, id=id)
        if not Follow.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'Подписки не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class RecipeViewSet(ModelViewSet):
    """Для работы с рецептами."""
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    #permission_classes = (AuthorOrStaffOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            for slug in tags:
                queryset = queryset.filter(tags__slug=slug)
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart in True:
             queryset = queryset.filter(cart=user.id)
        else:
            queryset = queryset.exclude(favorite=user.id)
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in True:
            queryset = queryset.filter(favorite=user.id)
        else:
            queryset = queryset.exclude(favorite=user.id)

        return queryset


    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path='(?P<recipe_pk>[^/.]+)/favorite',
    )
    def favorite(self, request, pk=None):
        """Добавляет/удаляет рецепт в Избранное."""
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            user.wish_list.add(recipe)
            return Response(
                'Рецепт добавлен в избранное',
                status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)

            if recipe in user.wish_list.all():
                user.wish_list.remove(recipe)
                return Response(
                    'Рецепт удалён из избранного',
                    status=status.HTTP_204_NO_CONTENT
                )

            return Response(
                'Рецепта нет в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path='(?P<recipe_pk>[^/.]+)/shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет/удаляет рецепт в Списке покупок."""
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            user.shop_list.add(recipe)
            return Response(
                'Рецепт добавлен в список покупок',
                status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            if recipe in user.shop_list.all():
                user.shop_list.remove(recipe)
                return Response(
                    'Рецепт удалён из список покупок',
                    status=status.HTTP_204_NO_CONTENT
                )

            return Response(
                'Рецепта нет в списке покупок',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""
        user = request.user
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
                f'{ingredient["ingredient"]}: {ingredient["amount"]} {ingredient["measurement_unit"]}\n'
            )

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    

class TagViewSet(ReadOnlyModelViewSet):
    """Для работы с тэгами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self):
        """Реализован поиск объектов по совпадению в начале названия,
        также добавляются результаты по совпадению в середине.
        """
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            name = name.lower()
            stw = list(queryset.filter(name__startswith=name))
            cnt = queryset.filter(name__contains=name)
            stw.extend(
                [val for val in cnt if val not in stw]
            )
            queryset = stw
        return queryset

