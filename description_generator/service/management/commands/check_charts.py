from django.core.management.base import BaseCommand

from service.services import check_charts


class Command(BaseCommand):

    def handle(self, *args, **options):
        check_charts()
