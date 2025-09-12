from rest_framework import viewsets, permissions
from students.models import StudentsProjection
from .serializers import StudentsProjectionSerializer
from django.db import connection

class StudentsProjectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentsProjection.objects.all().order_by("-updated_at")
    serializer_class = StudentsProjectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        min_gpa = params.get("min_gpa")
        skills = [s.strip() for s in (params.get("skills") or "").split(",") if s.strip()]
        lang = params.get("lang")

        if connection.vendor == "postgresql":
            if min_gpa:
                qs = qs.filter(**{"data__gpa__gte": float(min_gpa)})
            if skills:
                qs = qs.filter(**{"data__skills__contains": skills})
            if lang:
                qs = qs.filter(**{"data__language": lang})
            return qs

        # Фоллбек для других БД (на всякий)
        data = list(qs)
        ids = []
        for r in data:
            d = r.data or {}
            if min_gpa and float(d.get("gpa", -1e9)) < float(min_gpa):
                continue
            if lang and d.get("language") != lang:
                continue
            if skills and not set(skills).issubset(set(d.get("skills", []))):
                continue
            ids.append(r.pk)
        return qs.model.objects.filter(pk__in=ids).order_by("-updated_at")
