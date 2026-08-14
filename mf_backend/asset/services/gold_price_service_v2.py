import datetime
from datetime import timedelta as timedelta
from lender.models import Lender
from lender.serializers import LenderGoldPriceSerializer
from asset.models import GoldPriceData, GoldPriceHistory
from asset.serializers import GoldPriceSerializer
from utility.common_utils import custom_response_obj
from utility.crud_helper import CrudHelper


class GoldPriceServiceV2:

    crud_helper = CrudHelper(GoldPriceSerializer)

    def get_price(self):
        lendersGoldPrice = Lender.objects.all()
        resp = LenderGoldPriceSerializer(lendersGoldPrice, many=True).data
        return custom_response_obj(message={"lenders": resp}, code=200)

    def add_data(self, data):
        for karat_data in data:
            try:
                # gold_data = GoldPriceData.objects.get(
                #     karat=karat_data.get("karat"),
                #     lender=karat_data.get("lender").get("lender_id"),
                # )
                gold_data = GoldPriceData.objects.get(
                    gold_price_id=karat_data.get("gold_price_id"),
                )
                if float(gold_data.gold_price) != float(karat_data.get("gold_price")):
                    gold_data.gold_price = karat_data.get("gold_price")
                    # gold_data.modified_at = datetime.datetime.now()
                    gold_data.save()
                    self.__populate_gold_changes_history(
                        karat_data={
                            "gold_price": gold_data.old_gold_price,
                            "karat": gold_data.karat,
                            "lender": gold_data.lender,
                        }
                    )

            except GoldPriceData.DoesNotExist as e:
                return custom_response_obj(message=str(e), code=403)

        data = self.get_price()
        # return custom_response_obj(message=data, code=200)
        return data

    def __populate_gold_changes_history(self, karat_data):
        resp = []

        gold_data = GoldPriceHistory(**karat_data)
        gold_data.save()
        resp.append(gold_data)
        return resp
