import traceback

from django.core.management import BaseCommand

from loan.models import GprsPhotos


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            gprs=GprsPhotos.objects.all()
            for i in gprs:
                take_over_data=i.take_over_residence
                if take_over_data is not None:
                    account_id=take_over_data.account
                    if account_id is not None:
                        i.account=account_id
                        i.save()
        except:
            traceback.print_exc()

