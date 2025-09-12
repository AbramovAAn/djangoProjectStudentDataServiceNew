from django.db import models
from django.utils import timezone

class Consent(models.Model):
    PURPOSE_PLACEMENT = "placement"
    PURPOSE_CHOICES = [
        (PURPOSE_PLACEMENT, "Распределение на практику"),
    ]

    # Привязка к нашему student_id из витрины (UUID в StudentsProjection)
    student_id = models.UUIDField(db_index=True)
    purpose = models.CharField(max_length=64, choices=PURPOSE_CHOICES)
    granted = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student_id", "purpose")
        db_table = "consents"

    def is_active(self) -> bool:
        if not self.granted:
            return False
        if self.expires_at and self.expires_at <= timezone.now():
            return False
        return True

