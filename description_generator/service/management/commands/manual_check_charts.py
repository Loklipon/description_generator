from django.core.management.base import BaseCommand

from service.charts_services import get_departments, get_nomenclature, check_charts
from service.models import Config


class Command(BaseCommand):

    def handle(self, *args, **options):

        config = Config.objects.first()
        if config.check_button:
            if not config.process:
                config.process = True
                config.save()
                try:
                    if get_departments() and get_nomenclature():
                        check_charts()
                except Exception as e:
                    print(e)
                finally:
                    config.check_button = False
                    config.save()
                    config.process = False
                    config.save()
