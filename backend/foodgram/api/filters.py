from distutils.util import strtobool

from django_filters import rest_framework
from recipe.models import FavoriteRecipe, Recipe, ShoppingList, Tag
from rest_framework.filters import SearchFilter

CHOICES_VALUE = (
    ('0', 'False'),
    ('1', 'True')
)


class CustomIngredientsSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_VALUE,
        method='get_is_favorited'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_VALUE,
        method='get_is_in_shopping_cart'
    )
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()
        favorites_recipe = FavoriteRecipe.objects.filter(
            user=self.request.user)
        recipes = [val.recipe.id for val in favorites_recipe]
        new_queryset = queryset.filter(id__in=recipes)
        if not strtobool(value):
            return queryset.difference(new_queryset)
        return queryset.filter(id__in=recipes)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [val.recipe.id for val in shopping_cart]
        new_queryset = queryset.filter(id__in=recipes)
        if not strtobool(value):
            return queryset.difference(new_queryset)
        return queryset.filter(id__in=recipes)
