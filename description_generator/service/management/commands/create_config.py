from django.core.management.base import BaseCommand

from service.models import Config


class Command(BaseCommand):

    def handle(self, *args, **options):
        Config.objects.create()
