from rest_framework import filters


class CustomIngredientsSearchFilter(filters.SearchFilter):
    search_param = 'name'
