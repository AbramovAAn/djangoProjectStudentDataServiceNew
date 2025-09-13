import os
import sys
import django
import secrets

# >>> добавили 3 строки: поднимаем BASE_DIR в sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# <<<

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sds.settings")
django.setup()

from integrations.models import ApiClient  # noqa: E402

raw = secrets.token_urlsafe(32)

client, _ = ApiClient.objects.get_or_create(
    name="practice-matcher",
    defaults={"scopes": ["students:write"]},
)

client.set_key(raw)
client.is_active = True
client.save()

print("API_KEY=", raw)
print("prefix =", client.prefix)