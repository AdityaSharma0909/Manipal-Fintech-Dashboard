from django.core.management.base import BaseCommand

from product.models import WhiteGoods
from utils.constants import RADIAN_OFFICE_IN_INDIA
from utils.envSetup import environment



class Command(BaseCommand):

    def handle(self, *args, **options):
        WhiteGoods.objects.all().update(available_in=RADIAN_OFFICE_IN_INDIA)


