from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StudentsProjectionViewSet, StudentsIngestView
from consents.views import ConsentGrantView, ConsentRevokeView

router = DefaultRouter()
router.register(r"students", StudentsProjectionViewSet, basename="students")

urlpatterns = [
    # Сначала узкоспециализированные маршруты
    path("students/ingest/", StudentsIngestView.as_view(), name="students_ingest"),

    # Затем — все, что даёт router (list/detail /api/v1/students/…)
    path("", include(router.urls)),

    # Остальные ручки
    path("consents/grant/",  ConsentGrantView.as_view(),   name="consent_grant"),
    path("consents/revoke/", ConsentRevokeView.as_view(),  name="consent_revoke"),
]
