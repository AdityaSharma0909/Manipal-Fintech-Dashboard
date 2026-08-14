import datetime
import traceback
from django.utils import timezone
from datetime import timedelta as timedelta
from django.core.exceptions import ObjectDoesNotExist
from lender.models import Lender
from django.db.models import OuterRef, Subquery
from asset.models import GoldPriceData, GoldPriceHistory
from asset.serializers import GoldPriceSerializer, GoldPriceModelSerializer
from utility.common_utils import custom_response_obj
from utility.crud_helper import CrudHelper
from utils.responseHandler import HttpResponse


class GoldPriceService:

    crud_helper = CrudHelper(GoldPriceSerializer)

    def get_price(self):
        # # from django.db.models import CharField
        # latest_created_at_subquery = GoldPriceData.objects.filter(
        #     karat=OuterRef('karat')
        # ).order_by('-created_at').values('created_at')[:1]

        # # Query to get the latest entry for each distinct karat
        # latest_entries = GoldPriceData.objects.filter(
        #     created_at=Subquery(latest_created_at_subquery)
        # )

        # # return self.crud_helper.get_all_data(query=Q(**{}),
        # #                                      annotate={'date':Max('created_at'),
        # #                                                'current_gold_price_today':F('gold_price'),
        # #                                                'current_lending_price':F('lending_price'),
        # #                                               'id':StringAgg(Cast('gold_price_id',output_field=CharField()),delimiter=",")},
        # #                                      values_list=('karat',))

        gold_prices = GoldPriceData.objects.all()
        data = GoldPriceModelSerializer(gold_prices, many=True).data
        date_week_behind = timezone.now() - timedelta(days=7)
        history_data = list(
            GoldPriceHistory.objects.values().filter(created_at__gte=date_week_behind)
        )
        GoldPriceHistory.objects.filter(created_at__lt=date_week_behind).delete()
        for i in data:
            karat_data = list(
                filter(lambda x: x["karat"] == i.get("karat"), history_data)
            )
            i["historical_data"] = karat_data
        return custom_response_obj(message=data, code=200)

    # def update_data(self, data, id):
    #     return self.crud_helper.update_obj(data=data,update_key_value=id)

    def add_data(self, data):
        for karat_data in data:
            try:
                gold_data = GoldPriceData.objects.get(
                    karat=karat_data.get("karat"),
                    lender=karat_data.get("lender").get("lender_id"),
                )
                if float(gold_data.gold_price) != float(karat_data.get("gold_price")):
                    gold_data.gold_price = karat_data.get("gold_price")
                    # gold_data.old_gold_price = karat_data.get("old_gold_price")
                    gold_data.modified_at = datetime.datetime.now()
                    gold_data.save()
                    self.__populate_gold_changes_history(
                        karat_data={
                            "gold_price": gold_data.old_gold_price,
                            "karat": gold_data.karat,
                            # "lender": Lender(**karat_data.get("lender")),
                            "lender": gold_data.lender,
                        }
                    )

            except GoldPriceData.DoesNotExist as e:
                return custom_response_obj(message=str(e), code=403)
                # gold_data = GoldPriceData(**karat_data)
                # gold_data.save()

        data = self.get_price()
        return custom_response_obj(message=data, code=200)

    def __populate_gold_changes_history(self, karat_data):
        resp = []

        gold_data = GoldPriceHistory(**karat_data)
        gold_data.save()
        # gold_data = GoldPriceHistory.objects.create(
        #     gold_price=data["gold_price"],
        #     karat=data["karat"],
        #     lender=data["lender__lender_id"],
        # )
        resp.append(gold_data)
        return resp
