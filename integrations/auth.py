from typing import Optional, Tuple
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import ApiClient

class ServiceUser:
    """Лёгкий 'пользователь' для DRF. Умеет только is_authenticated и client."""
    is_authenticated = True
    def __init__(self, client: ApiClient):
        self.client = client
        self.username = f"service:{client.name}"
class APIKeyAuthentication(BaseAuthentication):
    """
    Принимаем:
      Authorization: ApiKey <raw-key>
      или
      X-Api-Key: <raw-key>
    """
    keyword = "ApiKey"

    def authenticate(self, request) -> Optional[Tuple[ServiceUser, None]]:
        key = None
        auth = get_authorization_header(request).decode("utf-8")
        if auth and auth.startswith(self.keyword + " "):
            key = auth[len(self.keyword) + 1:].strip()
        if not key:
            key = request.headers.get("X-Api-Key")

        if not key:
            return None  # не предъявлял ключ — пусть другие аутентификации попробуют

        client = ApiClient.get_by_key(key)
        if not client:
            raise AuthenticationFailed(_("Invalid API key"))
        if not client.is_active:
            raise AuthenticationFailed(_("Client disabled"))

        # Запомним, кто это, и отметим использование
        request.api_client = client
        ApiClient.objects.filter(pk=client.pk).update(last_used_at=timezone.now())
        return ServiceUser(client), None