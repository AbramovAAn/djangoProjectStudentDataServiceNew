import uuid
from django.db import models
from django.utils import timezone
import hashlib



EVENT_STUDENT_UPDATED = "student.updated"
EVENT_CONSENT_CHANGED = "consent.changed"
EVENT_CHOICES = [
    (EVENT_STUDENT_UPDATED, "Student updated"),
    (EVENT_CONSENT_CHANGED, "Consent changed"),
]

class WebhookEndpoint(models.Model):
    """Получатель вебхуков."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    # Список событий, на которые подписан эндпоинт
    events = models.JSONField(default=list)   # ["student.updated", "consent.changed"]
    secret = models.CharField(max_length=128) # общий секрет для HMAC
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "webhook_endpoints"

    def listens(self, event: str) -> bool:
        return self.is_active and (event in (self.events or []))

class WebhookDelivery(models.Model):
    """Очередь доставок + лог."""
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="deliveries")
    event = models.CharField(max_length=64, choices=EVENT_CHOICES)
    payload = models.JSONField()
    headers = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, default=STATUS_PENDING)
    attempts = models.IntegerField(default=0)
    last_status_code = models.IntegerField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    next_retry_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "webhook_deliveries"
        indexes = [
            models.Index(fields=["status", "next_retry_at"]),
        ]
class ApiClient(models.Model):
    """
    Сервисный клиент с API-ключом и скоупами.
    Сам ключ храним в виде SHA256 (key_hash). Сырой ключ не сохраняем.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    scopes = models.JSONField(default=list, blank=True)  # напр.: ["students:write"]
    prefix = models.CharField(max_length=12, blank=True) # первые символы ключа для отладки
    key_hash = models.CharField(max_length=64)           # sha256(raw_key)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "api_clients"

    # --- helpers ---
    @staticmethod
    def _hash(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def set_key(self, raw_key: str):
        self.key_hash = self._hash(raw_key)
        self.prefix = raw_key[:8]

    @classmethod
    def get_by_key(cls, raw_key: str):
        if not raw_key:
            return None
        h = cls._hash(raw_key)
        try:
            return cls.objects.get(key_hash=h, is_active=True)
        except cls.DoesNotExist:
            return None