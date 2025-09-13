from rest_framework.permissions import BasePermission

class HasServiceScope(BasePermission):
    """
    Проверяет, что у клиента есть нужный скоуп.
    Вью может задать атрибут required_scope = "..."
    """
    message = "Missing required service scope."

    def has_permission(self, request, view) -> bool:
        client = getattr(request, "api_client", None)
        if not client:
            return False
        required = getattr(view, "required_scope", None)
        if not required:
            return True  # скоуп не задан — разрешаем
        return required in (client.scopes or [])
