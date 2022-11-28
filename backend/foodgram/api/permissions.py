from rest_framework import permissions

class AdminOrReadOnly(permissions.BasePermission):
    """Разрешение на создание и редактирование только для администратора.
    Для остальных только чтение.
    """
    message = 'У вас недостаточно прав для выполнения данного действия.'
    
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                and request.user.is_authenticated
                )

