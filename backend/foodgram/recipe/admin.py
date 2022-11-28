from django.contrib import admin
from .models import AmountIngredient, Tag, Ingredient, Recipe


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
    #readonly_fields = ("wish_list_count",)
    empty_value_display = '-пусто-' 

