import uuid
from django.db import models
from django.utils import timezone

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
