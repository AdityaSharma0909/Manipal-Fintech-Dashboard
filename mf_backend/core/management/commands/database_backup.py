from django.core.management import BaseCommand
from core.service.database_backup import BackDatabase


class Command(BaseCommand):

    def handle(self, *args, **options):
        BackDatabase().backup()

