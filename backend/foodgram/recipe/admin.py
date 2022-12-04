from django.contrib import admin

from .models import (AmountIngredient, FavoriteRecipe, Ingredient, Recipe,
                     ShoppingList, Tag)


class RecipeIngredientsInLine(admin.TabularInline):
    model = AmountIngredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'color', 'slug',
    )
    list_filter = (
        'name',
    )
    search_fields = (
        'name', 'color'
    )
    empty_value_display = '-пусто-'
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredients', 'amount',
    )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    search_fields = (
        'name', 'author',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
    inlines = [RecipeIngredientsInLine]
    empty_value_display = '-пусто-'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'
