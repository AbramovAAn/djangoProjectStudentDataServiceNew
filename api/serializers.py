# api/serializers.py
from rest_framework import serializers
from students.models import StudentsProjection

class StudentsProjectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentsProjection
        fields = ["student_id", "data", "updated_at"]

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