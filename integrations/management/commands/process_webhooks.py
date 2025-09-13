from django.core.management.base import BaseCommand
from django.utils import timezone
from integrations.models import WebhookDelivery
from integrations.webhooks import send_delivery
import time

class Command(BaseCommand):
    help = "Отправка очереди вебхуков (pending). По умолчанию один проход. С --loop работает как воркер."

    def add_arguments(self, parser):
        parser.add_argument("--batch", type=int, default=50, help="Сколько записей брать за раз")
        parser.add_argument("--loop", action="store_true", help="Работать циклом")
        parser.add_argument("--sleep", type=int, default=5, help="Пауза между циклами, сек")

    def handle(self, *args, **opts):
        batch = opts["batch"]
        looping = opts["loop"]
        sleep_s = opts["sleep"]

        def run_once():
            now = timezone.now()
            qs = (WebhookDelivery.objects
                  .select_related("endpoint")
                  .filter(status=WebhookDelivery.STATUS_PENDING, next_retry_at__lte=now)
                  .order_by("next_retry_at")[:batch])
            for d in qs:
                send_delivery(d)

        if looping:
            self.stdout.write(self.style.SUCCESS("Webhook worker started ... Ctrl+C to stop"))
            try:
                while True:
                    run_once()
                    time.sleep(sleep_s)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("Worker stopped"))
        else:
            run_once()
