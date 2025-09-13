import secrets
from integrations.models import ApiClient
raw = secrets.token_urlsafe(32)
c, _ = ApiClient.objects.get_or_create(name="practice-matcher", defaults={"scopes": ["students:write"]})
c.set_key(raw); c.is_active=True; c.save()
print("API_KEY=", raw)
print("prefix =", c.prefix)