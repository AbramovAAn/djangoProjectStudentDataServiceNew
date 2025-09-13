from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Consent
from integrations.models import EVENT_CONSENT_CHANGED
from integrations.webhooks import fire_and_forget

@receiver(post_save, sender=Consent)
def on_consent_changed(sender, instance: Consent, created, **kwargs):
    data = {
        "student_id": str(instance.student_id),
        "purpose": instance.purpose,
        "granted": instance.granted,
        "expires_at": instance.expires_at.isoformat() if instance.expires_at else None,
        "updated_at": instance.updated_at.isoformat() if instance.updated_at else None,
        "created": bool(created),
    }
    fire_and_forget(EVENT_CONSENT_CHANGED, data)
