from django.core.management.base import BaseCommand

from service.services import create_organizations


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_organizations()
