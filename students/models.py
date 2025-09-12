from django.db import models

# Create your models here.
import uuid
from django.db import models

class StudentsProjection(models.Model):
    student_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.JSONField()          # {"fio":"...", "gpa":8.1, "skills":[...], "language":"en"}
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students_projection"