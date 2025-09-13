import hmac, hashlib, json, time, uuid
from typing import Dict, Any
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import requests

from .models import WebhookEndpoint, WebhookDelivery

WEBHOOK_TIMEOUT = getattr(settings, "WEBHOOK_TIMEOUT_SECONDS", 5)
USER_AGENT = getattr(settings, "WEBHOOK_USER_AGENT", "SDS-Webhooks/1.0")

def _sign(secret: str, timestamp: str, body_bytes: bytes) -> str:
    # подпись: sha256=HEX( HMAC_SHA256(secret, f"{timestamp}.{body}") )
    msg = timestamp.encode("utf-8") + b"." + body_bytes
    digest = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return f"sha256={digest}"

def enqueue_event(event: str, data: Dict[str, Any]):
    """
    Создаёт WebhookDelivery для каждого активного endpoint'а, подписанного на событие.
    Вызывается из сигналов (после commit).
    """
    endpoints = WebhookEndpoint.objects.filter(is_active=True)
    items = []
    for ep in endpoints:
        if not ep.listens(event):
            continue
        payload = {
            "id": str(uuid.uuid4()),
            "event": event,
            "produced_at": timezone.now().isoformat(),
            "data": data,
        }
        items.append(WebhookDelivery(endpoint=ep, event=event, payload=payload))
    if items:
        WebhookDelivery.objects.bulk_create(items, batch_size=500)

def _compute_backoff(attempts: int) -> int:
    # 30s, 60s, 120s, 240s, ... максимум 1 час
    return min(3600, 30 * (2 ** max(0, attempts-1)))

def send_delivery(delivery: WebhookDelivery) -> WebhookDelivery:
    """
    Единичная попытка доставки (вызов из воркера).
    """
    ep = delivery.endpoint
    body = json.dumps(delivery.payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ts = str(int(time.time()))
    signature = _sign(ep.secret, ts, body)
    hdrs = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "X-Webhook-Event": delivery.event,
        "X-Webhook-Id": delivery.payload.get("id", str(delivery.id)),
        "X-Webhook-Timestamp": ts,
        "X-Webhook-Signature": signature,
    }

    try:
        resp = requests.post(ep.url, data=body, headers=hdrs, timeout=WEBHOOK_TIMEOUT)
        delivery.attempts += 1
        delivery.headers = hdrs
        delivery.last_status_code = resp.status_code
        delivery.last_error = ""
        if 200 <= resp.status_code < 300:
            delivery.status = WebhookDelivery.STATUS_SENT
        else:
            delivery.status = WebhookDelivery.STATUS_PENDING
            delivery.next_retry_at = timezone.now() + timezone.timedelta(seconds=_compute_backoff(delivery.attempts))
    except Exception as e:
        delivery.attempts += 1
        delivery.headers = hdrs
        delivery.last_error = repr(e)
        delivery.status = WebhookDelivery.STATUS_PENDING
        delivery.next_retry_at = timezone.now() + timezone.timedelta(seconds=_compute_backoff(delivery.attempts))

    delivery.save(update_fields=["attempts","headers","last_status_code","last_error","status","next_retry_at","updated_at"])
    return delivery

def fire_and_forget(event: str, data: dict) -> None:
    """
    Корректно ставим задачу после успешного commit'а.
    Если транзакции нет — выполняем сразу.
    """
    if transaction.get_connection().in_atomic_block:
        transaction.on_commit(lambda: enqueue_event(event, data))
    else:
        enqueue_event(event, data)
