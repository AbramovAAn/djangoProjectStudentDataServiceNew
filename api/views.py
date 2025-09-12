# api/views.py
from typing import Dict, Any, List
from django.db import connection
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from consents.utils import should_mask, mask_student_data
from students.models import StudentsProjection
from .serializers import (
    StudentsProjectionSerializer,
    EligibilityRequestSerializer,
    EligibilityResponseSerializer,
)

def _score_student(sdata: Dict[str, Any], criteria: Dict[str, Any]) -> (float, Dict[str, Any]):
    # значения по умолчанию для весов
    w = {
        "gpa": 1.0,
        "skill": 1.0,
        "language": 0.2,
        "program": 0.2,
        "course": 0.2,
    }
    w.update(criteria.get("weights") or {})

    score = 0.0
    reasons = {}

    # GPA
    gpa = float(sdata.get("gpa") or 0.0)
    min_gpa = float(criteria.get("min_gpa") or 0.0)
    if gpa >= min_gpa:
        add = (gpa - min_gpa) * w["gpa"]
        score += add
        reasons["gpa_bonus"] = round(add, 3)
    else:
        reasons["gpa_penalty"] = round((min_gpa - gpa) * w["gpa"], 3)

    # Skills
    req_skills: List[str] = [s.strip().lower() for s in (criteria.get("skills") or []) if s.strip()]
    have_skills = set([str(x).lower() for x in (sdata.get("skills") or [])])
    matched = sorted(list(have_skills.intersection(req_skills)))
    missing = [s for s in req_skills if s not in have_skills]
    add = len(matched) * w["skill"]
    score += add
    reasons["skills_matched"] = matched
    reasons["skills_missing"] = missing
    reasons["skills_bonus"] = round(add, 3)

    # Language
    lang = (criteria.get("language") or "").strip()
    if lang:
        if str(sdata.get("language") or "").strip().lower() == lang.lower():
            score += w["language"]
            reasons["language_match"] = True
        else:
            reasons["language_match"] = False

    # Program
    prog = (criteria.get("program") or "").strip()
    if prog:
        if str(sdata.get("program") or "").strip().lower() == prog.lower():
            score += w["program"]
            reasons["program_match"] = True
        else:
            reasons["program_match"] = False

    # Course in range
    course = sdata.get("course")
    cmin = criteria.get("course_min")
    cmax = criteria.get("course_max")
    if course is not None and (cmin or cmax):
        ok_min = (cmin is None) or (course >= cmin)
        ok_max = (cmax is None) or (course <= cmax)
        if ok_min and ok_max:
            score += w["course"]
            reasons["course_match"] = True
        else:
            reasons["course_match"] = False

    return score, reasons

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

        # Фоллбэк для других БД
        data = list(qs); ids = []
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

    @action(detail=False, methods=["post"])
    def eligibility(self, request):
        """
        Ранжирование студентов по заданным критериям.
        Тело запроса: EligibilityRequestSerializer.
        """
        req = EligibilityRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        criteria = req.validated_data

        qs = self.get_queryset()  # применим базовые фильтры, если передавали в query params
        items = []
        for sp in qs:
            sdata = sp.data or {}
            # маскирование по согласию/роли
            if should_mask(request, sp.student_id):
                sdata = mask_student_data(sdata)

            score, reasons = _score_student(sdata, criteria)
            items.append({
                "student_id": sp.student_id,
                "score": round(score, 3),
                "explanations": reasons,
                "data": sdata,
            })
        items.sort(key=lambda x: x["score"], reverse=True)
        limit = criteria.get("limit", 50)
        resp = {
            "criteria": criteria,
            "count": len(items),
            "results": items[:limit],
        }
        return Response(EligibilityResponseSerializer(resp).data)
