from django.contrib import admin
from .models import UserProfile, Follow


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    fields = (
        ('username', 'email', ),
        ('first_name', 'last_name', ),
    )
    list_display = (
        'username', 'email', 'first_name', 'last_name',
    )
    list_display_links = ('first_name', 'last_name')
    search_fields = (
        'username', 'email',
    )
    list_filter = (
        'first_name', 'email',
    )
    empty_value_display = '-пусто-' 

admin.site.register(Follow)