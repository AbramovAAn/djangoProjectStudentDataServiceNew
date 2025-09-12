from rest_framework import serializers
from .models import Consent

class ConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consent
        fields = ["student_id", "purpose", "granted", "expires_at", "updated_at"]

class ConsentGrantSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    purpose = serializers.ChoiceField(choices=Consent.PURPOSE_CHOICES, default=Consent.PURPOSE_PLACEMENT)
    granted = serializers.BooleanField(default=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

class ConsentRevokeSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    purpose = serializers.ChoiceField(choices=Consent.PURPOSE_CHOICES, default=Consent.PURPOSE_PLACEMENT)
