from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentsProjectionViewSet

router = DefaultRouter()
router.register(r"students", StudentsProjectionViewSet, basename="students")

urlpatterns = [path("", include(router.urls))]