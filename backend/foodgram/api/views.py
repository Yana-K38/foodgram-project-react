from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from recipe.models import Tag, Ingredient, Recipe
from user.models import UserProfile
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, UserProfileSerializer
from .permissions import AdminOrReadOnly

class UserProfileViewSet(ReadOnlyModelViewSet):
    """Для работы с пользователями."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RecipeViewSet(ReadOnlyModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    

class TagViewSet(ReadOnlyModelViewSet):
    """Работа с тэгами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работа с ингредиентами."""
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

