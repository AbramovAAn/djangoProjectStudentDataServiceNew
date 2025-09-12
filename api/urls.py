from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentsProjectionViewSet
from consents.views import ConsentGrantView, ConsentRevokeView
router = DefaultRouter()
router.register(r"students", StudentsProjectionViewSet, basename="students")

urlpatterns = [path("", include(router.urls))]
router = DefaultRouter()
router.register(r"students", StudentsProjectionViewSet, basename="students")

urlpatterns = [
    path("", include(router.urls)),
    path("consents/grant/", ConsentGrantView.as_view(), name="consent_grant"),
    path("consents/revoke/", ConsentRevokeView.as_view(), name="consent_revoke"),
]