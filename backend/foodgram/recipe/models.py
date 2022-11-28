from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Tag(models.Model):
    """Теги для рецептов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Тег'
    )
    color = models.CharField(
        max_length=7,
        default='FF',
        null=True,
        verbose_name='HEX-код',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='URL',
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Ингредиенты для рецепта."""
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

class AmountIngredient(models.Model):
    """Модель связывает Recipe и Ingredient
    с указанием количества ингредиента.
    """
    recipe = models.ForeignKey(
        'Recipe',
        related_name='recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        'Ingredient',
        related_name='recipe_am',
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=[MinValueValidator(
            1, 'Минимальное значение 1'
        )
        ]
    )
    
    class Meta:
        ordering = ['recipe']

    def __str__(self):
        return f'{self.amount} {self.ingredients}'


class Recipe(models.Model):
    """Модель для описания рецепта."""
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
        related_name='recipe',
        through='AmountIngredient',
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
    favorite = models.ManyToManyField(
        User,
        verbose_name='Понравившийся рецепт',
        related_name='favorites',
    )


    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name
    
