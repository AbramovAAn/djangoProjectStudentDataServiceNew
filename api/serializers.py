# api/serializers.py
from rest_framework import serializers
from students.models import StudentsProjection

class StudentsProjectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentsProjection
        fields = ["student_id", "data", "updated_at"]