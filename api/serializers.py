# api/serializers.py
from students.models import StudentsProjection
from consents.utils import should_mask, mask_student_data
import re
from rest_framework import serializers
from metadata.models import StudyProgram, Skill, Language

class StudentsProjectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentsProjection
        fields = ["student_id", "data", "updated_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")
        if request and should_mask(request, instance.student_id):
            rep["data"] = mask_student_data(rep["data"])
        return rep
class EligibilityRequestSerializer(serializers.Serializer):
    min_gpa = serializers.FloatField(required=False, default=0.0)
    language = serializers.CharField(required=False, allow_blank=True, default="")
    program = serializers.CharField(required=False, allow_blank=True, default="")
    course_min = serializers.IntegerField(required=False, min_value=1, default=None)
    course_max = serializers.IntegerField(required=False, min_value=1, default=None)
    skills = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    # Веса: {"gpa": 1.0, "skill": 1.0, "language": 0.2, "program": 0.2}
    weights = serializers.DictField(required=False, default=dict)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=500, default=50)

class EligibilityItemSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    score = serializers.FloatField()
    explanations = serializers.DictField()
    data = serializers.DictField()

class EligibilityResponseSerializer(serializers.Serializer):
    criteria = EligibilityRequestSerializer()
    count = serializers.IntegerField()
    results = EligibilityItemSerializer(many=True)
class StudentWriteSerializer(serializers.Serializer):
    student_id = serializers.UUIDField(required=False)
    data = serializers.DictField()

    def validate_data(self, v: dict) -> dict:
        # Мягкая валидация базовых полей
        gpa = v.get("gpa")
        if gpa is not None:
            try:
                g = float(gpa)
            except Exception:
                raise serializers.ValidationError({"gpa": "Must be a number"})
            if not (0 <= g <= 10):
                raise serializers.ValidationError({"gpa": "Must be between 0 and 10"})

        course = v.get("course")
        if course is not None and (not isinstance(course, int) or course < 1 or course > 6):
            raise serializers.ValidationError({"course": "Must be integer 1..6"})

        skills = v.get("skills")
        if skills is not None and not isinstance(skills, list):
            raise serializers.ValidationError({"skills": "Must be a list of strings"})

        lang = v.get("language")
        if lang is not None and lang not in ("en", "ru"):
            raise serializers.ValidationError({"language": "Allowed: 'en' or 'ru'"})

        # сюда позже добавить проверки по справочникам metadata .*
        return v
class StudentPayloadSerializer(serializers.Serializer):
    fio     = serializers.CharField(max_length=255)
    program = serializers.SlugRelatedField(slug_field="name", queryset=StudyProgram.objects.filter(is_active=True))
    course  = serializers.IntegerField(min_value=1, max_value=6)
    gpa     = serializers.FloatField(min_value=0.0, max_value=10.0)
    skills  = serializers.ListField(
        child=serializers.SlugRelatedField(slug_field="code", queryset=Skill.objects.filter(is_active=True)),
        allow_empty=True
    )
    language = serializers.SlugRelatedField(slug_field="code", queryset=Language.objects.filter(is_active=True))
    note     = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_fio(self, v: str):
        # простая проверка ФИО: буквы, пробелы, дефисы, минимум 5 символов
        if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-\s']{5,}", v):
            raise serializers.ValidationError("Некорректное ФИО")
        return v

    def to_internal_value(self, data):
        # нормализуем skills к списку строк (вместо объектов) после .is_valid()
        ret = super().to_internal_value(data)
        ret["skills"] = [s.code for s in ret["skills"]]
        ret["program"] = ret["program"].name
        ret["language"] = ret["language"].code
        return ret