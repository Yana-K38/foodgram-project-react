from django_filters import rest_framework
from django_filters.rest_framework import (NumberFilter,
                                           ModelMultipleChoiceFilter)
from rest_framework import filters

from recipe.models import Recipe, Tag


class CustomIngredientsSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = NumberFilter(method='get_in_favorited')
    is_in_shopping_list = NumberFilter(method='get_is_in_shopping_list')
    author = rest_framework.CharFilter(lookup_expr='exact')

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_list',
            'author', 'tags',
        )

    def get_in_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticaticated:
            return queryset.filter(
                favorite_in__user=self.request.user
            )
        return queryset.exclude(favorite_in__user=self.request.user)
        # return Recipe.objects.exclude(favorite_in__user=self.request.user)

    def get_is_in_shopping_list(self, queryset, name, value):
        if value and self.request.user.is_authenticaticated:
            return queryset.filter(
                in_shopping_list__user=self.request.user
            )
        return []
