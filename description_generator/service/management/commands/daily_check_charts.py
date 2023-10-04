from django.core.management.base import BaseCommand

from service.charts_services import get_departments, get_nomenclature, check_charts


class Command(BaseCommand):

    def handle(self, *args, **options):
        if get_departments() and get_nomenclature():
            check_charts()
