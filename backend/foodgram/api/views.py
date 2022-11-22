from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet


class RecipeViewSet(ReadOnlyModelViewSet):
    pass

class TagViewSet(ReadOnlyModelViewSet):
   pass


class IngredientViewSet(ReadOnlyModelViewSet):
    pass