from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

User = get_user_model()


class Tag(models.Model):
    """Теги для рецептов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Тег'
    )
    color = ColorField(
        max_length=10,
        default='FF0000',
        null=True,
        verbose_name='HEX-код',
        format="hexa",
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='URL',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Tag, self).save()


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
        validators=(
            MinValueValidator(
                1, 'Количество ингредиента не может быть меньше 1'
                ),),
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
        verbose_name='Название рецепта',
        unique=True,
    )
    image = models.ImageField(
        verbose_name='Фотография готового блюда',
        upload_to='recipe_img/',
        help_text='Загрузите фотографию'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipe',
        through='AmountIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        help_text='Выберите тег',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(
            1, 'Время приготовления рецепта не может быть меньше 1 минуты'
            ),),
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Понравившийся рецепт',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe',
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingList(models.Model):
    """Модель список покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_list',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list_recipe',
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'
