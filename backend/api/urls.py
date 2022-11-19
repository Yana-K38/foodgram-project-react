from django.urls import include, path
from rest_framework import routers
from .views import RecipeViewSet, TagViewSet, IngredientViewSet

router = routers.DefaultRouter()

router.register('recipe', RecipeViewSet, basename = 'recipe')
router.register('tags', TagViewSet, basename = 'tag')
router.register('ingredients', IngredientViewSet, basename = 'Ingredient')
#router.register('user', UserViewSet, basename = 'user')

urlpatterns = (
    path('', include(router.urls)),
)


