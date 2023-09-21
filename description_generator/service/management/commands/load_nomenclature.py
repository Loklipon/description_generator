from django.core.management.base import BaseCommand

from service.services import create_nomenclature_elements


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_nomenclature_elements()
