from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentsProjection
from integrations.models import EVENT_STUDENT_UPDATED
from integrations.webhooks import fire_and_forget

@receiver(post_save, sender=StudentsProjection)
def on_student_updated(sender, instance: StudentsProjection, created, **kwargs):
    # единый payload для внешних систем
    data = {
        "student_id": str(instance.student_id),
        "data": instance.data,
        "updated_at": instance.updated_at.isoformat() if instance.updated_at else None,
        "created": bool(created),
    }
    fire_and_forget(EVENT_STUDENT_UPDATED, data)
