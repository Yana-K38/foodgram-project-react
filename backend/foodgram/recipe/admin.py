from django.contrib import admin
from .models import AmountIngredient, Tag, Ingredient, Recipe

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(AmountIngredient)
