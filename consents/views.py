from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Consent
from .serializers import ConsentSerializer, ConsentGrantSerializer, ConsentRevokeSerializer

class ConsentGrantView(APIView):
    """
    Выдача/обновление согласия (требуется staff).
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        ser = ConsentGrantSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj, _created = Consent.objects.update_or_create(
            student_id=ser.validated_data["student_id"],
            purpose=ser.validated_data["purpose"],
            defaults={
                "granted": ser.validated_data.get("granted", True),
                "expires_at": ser.validated_data.get("expires_at"),
            }
        )
        return Response(ConsentSerializer(obj).data, status=status.HTTP_200_OK)

class ConsentRevokeView(APIView):
    """
    Отзыв согласия (требуется staff).
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        ser = ConsentRevokeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            obj = Consent.objects.get(
                student_id=ser.validated_data["student_id"],
                purpose=ser.validated_data["purpose"],
            )
            obj.granted = False
            obj.expires_at = None
            obj.save(update_fields=["granted", "expires_at", "updated_at"])
            return Response(ConsentSerializer(obj).data)
        except Consent.DoesNotExist:
            return Response({"detail": "Согласие не найдено"}, status=404)
