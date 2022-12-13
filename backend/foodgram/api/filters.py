from django_filters import rest_framework
from django_filters.rest_framework import (BooleanFilter,
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
    in_favorited = BooleanFilter(method='get_in_favorited')
    is_in_shopping_list = BooleanFilter(method='get_is_in_shopping_list')
    author = rest_framework.CharFilter(lookup_expr='exact')

    class Meta:
        model = Recipe
        fields = (
            'in_favorited',
            'is_in_shopping_list',
            'author', 'tags',
        )

    def get_in_favorited(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                favorite_in__user=self.request.user
            )
        return Recipe.objects.exclude(favorite_in__user=self.request.user)

    def get_is_in_shopping_list(self, queryset, name, value):
        if value:
            return queryset.filter(
                in_shopping_list__user=self.request.user
            )
