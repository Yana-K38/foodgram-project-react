from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import viewsets
from recipe.models import Tag, Ingredient, Recipe
from user.models import UserProfile
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, UserProfileSerializer

class UserProfileViewSet(ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RecipeViewSet(ReadOnlyModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    

class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
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

