from django.core.management.base import BaseCommand

from service.services import create_organizations, create_nomenclature_elements


class Command(BaseCommand):

    def handle(self, *args, **options):
        if create_organizations() and create_nomenclature_elements():
            # check_charts()
            pass
