from rest_framework import permissions


class AdminOrAuthor(permissions.BasePermission):
    """Разрешение на изменение только для админа и автора.
    """
    message = 'У вас недостаточно прав для выполнения данного действия.'

    # def has_permission(self, request, view):
    #     return (request.method in permissions.SAFE_METHODS
    #             or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user == obj.author)
         #   or request.user.is_superuser
        )


class AdminOrReadOnly(permissions.BasePermission):
    """Разрешение на изменение только для админа."""
    message = 'У вас недостаточно прав для выполнения данного действия.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)
