from rest_framework import permissions

class AdminOrReadOnly(permissions.BasePermission):
    """Разрешение на создание и редактирование только для администратора.
    Для остальных только чтение.
    """
    message = 'У вас недостаточно прав для выполнения данного действия.'
    
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin))

class AuthorOrStaffOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение на изменение только для админа и автора.
    Остальным только чтение.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user == obj.author)
            or request.user.is_staff
        )


