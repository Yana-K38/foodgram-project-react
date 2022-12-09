from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

router = routers.DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='Ingredient')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = (
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
)
