from django.contrib import admin

from .models import AmountIngredient, Tag, Ingredient, Recipe

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'pub_date', 'author')
    search_fields = ('name',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe,RecipeAdmin)
admin.site.register(AmountIngredient)