from django.core.management.base import BaseCommand

from service.charts_services import get_departments, get_nomenclature, check_charts
from service.models import Config


class Command(BaseCommand):

    def handle(self, *args, **options):

        config = Config.objects.first()

        if not config.process:
            config.process = True
            config.save()

            if get_departments() and get_nomenclature():
                check_charts()

            config.process = False
            config.save()
            config.check_button = False
            config.save()
