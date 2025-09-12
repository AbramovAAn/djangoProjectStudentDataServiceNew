from django.contrib import admin
from .models import Consent

@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "purpose", "granted", "expires_at", "updated_at")
    search_fields = ("student_id", "purpose")
    list_filter = ("purpose", "granted")
