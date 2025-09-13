from django.apps import AppConfig

class ConsentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "consents"
    verbose_name = "Consents"

    def ready(self):
        # подключаем сигналы согласий
        import consents.signals  # noqa
