from csv import reader

from django.core.management.base import BaseCommand

from recipe.models import Ingredient


class Command(BaseCommand):
    """Добавляем ингредиенты из файла CSV."""

    def handle(self, *args, **kwargs):
        with open(
                'recipe/data/ingredients.csv',
                encoding='UTF-8'
        ) as ingredients:
            for row in reader(ingredients):
                if len(row) == 2:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1],
                    )
