from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Тег'
    )
    color = models.CharField(
        max_length=10,
        default='FF',
        verbose_name='Цветовой HEX-код',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name='URL',
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name

class Recipe(models.Model):
    """Модель описывает рецепт."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipe_img/',
        help_text='Загрузите изображение'
    )
    text = models.TextField(
        verbose_name='Рецепт',
        help_text='Напишите рецепт',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name= 'Ингредиенты',
        related_name='recipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name
