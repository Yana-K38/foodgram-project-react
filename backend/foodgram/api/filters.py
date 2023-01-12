from distutils.util import strtobool

from django_filters import rest_framework
# from django_filters.rest_framework import (ModelMultipleChoiceFilter,
#                                            NumberFilter)
from recipe.models import FavoriteRecipe, Recipe, ShoppingList, Tag
from rest_framework import filters

CHOICES_LIST = (
    ('0', 'False'),
    ('1', 'True')
)


class CustomIngredientsSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_favorited_method'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_in_shopping_cart_method'
    )
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        favorites = FavoriteRecipe.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in favorites]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

# class RecipeFilter(rest_framework.FilterSet):
#     tags = ModelMultipleChoiceFilter(
#         field_name='tags__slug',
#         to_field_name='slug',
#         queryset=Tag.objects.all(),
#     )
#     is_favorited = NumberFilter(method='get_in_favorited')
#     is_in_shopping_list = NumberFilter(method='get_is_in_shopping_list')

#     class Meta:
#         model = Recipe
#         fields = (
#             'is_favorited',
#             'is_in_shopping_list',
#             'author', 'tags',
#         )

#     def get_in_favorited(self, queryset, name, value):
#         if value and self.request.user.is_authenticaticated:
#             return queryset.filter(
#                 favorite_in__user=self.request.user
#             )
#         return queryset.exclude(favorite_in__user=self.request.user)
#         # return Recipe.objects.exclude(favorite_in__user=self.request.user)

#     def get_is_in_shopping_list(self, queryset, name, value):
#         if value and self.request.user.is_authenticaticated:
#             return queryset.filter(
#                 in_shopping_list__user=self.request.user
#             )
#         return
