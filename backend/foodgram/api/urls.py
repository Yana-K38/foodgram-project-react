from django.urls import include, path
from rest_framework import routers
from .views import RecipeViewSet, TagViewSet, IngredientViewSet, UserProfileViewSet

router = routers.DefaultRouter()

router.register('recipe', RecipeViewSet, basename = 'recipe')
router.register('tags', TagViewSet, basename = 'tag')
router.register('ingredients', IngredientViewSet, basename = 'Ingredient')
router.register('users', UserProfileViewSet, basename = 'users')

urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
)
