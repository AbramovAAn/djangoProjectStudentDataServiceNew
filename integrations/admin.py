from django.contrib import admin
from .models import WebhookEndpoint, WebhookDelivery

@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("url", "is_active", "created_at")
    search_fields = ("url", "description")
    list_filter = ("is_active",)

@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("event", "endpoint", "status", "attempts", "last_status_code", "next_retry_at", "updated_at")
    list_filter = ("status", "event")
    search_fields = ("endpoint__url",)
    readonly_fields = ("payload", "headers", "created_at", "updated_at")
