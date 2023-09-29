from django.core.management.base import BaseCommand

from service.models import Config
from service.services import create_organizations, create_nomenclature_elements


class Command(BaseCommand):

    def handle(self, *args, **options):

        config = Config.objects.first()
        if config.check_button:
            try:
                if create_organizations() and create_nomenclature_elements():
                    # check_charts()
                    pass
            except Exception as e:
                print(e)
            finally:
                config.check_button = False
                config.save()
