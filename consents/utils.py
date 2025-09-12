from django.db.models import Q
from django.utils import timezone
from .models import Consent

MASK_SENSITIVE_KEYS = {"email", "phone", "address", "birthdate"}

def has_consent(student_id, purpose="placement") -> bool:
    now = timezone.now()
    return Consent.objects.filter(
        student_id=student_id,
        purpose=purpose,
        granted=True
    ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now)).exists()

def mask_student_data(data: dict) -> dict:
    """Маскируем ФИО и выкидываем явные ПДн (email/phone/address...)."""
    if not isinstance(data, dict):
        return data
    out = dict(data)
    # ФИО -> "Фамилия И.И."
    fio = out.get("fio")
    if isinstance(fio, str) and fio.strip():
        parts = fio.split()
        if len(parts) >= 2:
            initials = parts[1][0] + "."
            if len(parts) >= 3 and parts[2]:
                initials += parts[2][0] + "."
            out["fio"] = f"{parts[0]} {initials}"
        else:
            out["fio"] = fio[0] + "***"
    # явные ПДн — удаляем, если вдруг есть
    for k in list(out.keys()):
        if k.lower() in MASK_SENSITIVE_KEYS:
            out.pop(k, None)
    return out

def should_mask(request, student_id) -> bool:
    """Сотрудники (is_staff) видят всё; прочие — только при наличии согласия."""
    user = getattr(request, "user", None)
    if user and user.is_authenticated and user.is_staff:
        return False
    return not has_consent(student_id, purpose="placement")
