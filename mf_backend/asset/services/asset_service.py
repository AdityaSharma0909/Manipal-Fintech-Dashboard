from django.core.exceptions import ObjectDoesNotExist

from application.models import Application
from asset.serializers import AssetSingleSerializer
from utility.common_utils import custom_response_obj

from utils.helper import get_gold_price
from utils.constants import APPLICATION_STATUS, ASSET_DOCUMENT


class AssetService:

    def __get_application_instance(self, application_id):
        try:
            application = Application.objects.get(
                application_id=application_id)
            return application
        except ObjectDoesNotExist:
            return None


    def __create_payload(self, data, application):
        data["gross_weight"] = float(data["gross_weight"])
        data["net_weight"] = float(data["net_weight"])
        data["karat_value"] = int(data["karat_value"])
        data["application"] = str(application)
        data["leverage"] = 3
        # gold_price = helper.price_of_gold_22_karates()

        # gold_price = float(GoldPriceData.objects.values('gold_price').get(karat=data["karat_value"]).get('gold_price'))
        gold_price = get_gold_price(application.lender, data["karat_value"])

        # price_of_22_karate = gold_price
        # price_of_22_karate = float(price_of_22_karate["gold_price__avg"])
        data["marketvalueatappraisal"] = gold_price
        # data["net_weight_22k"] = round(
        #     helper.customer_gold_weight_converter_to_22_karate_weight(
        #         data["karat_value"], data["net_weight"]
        #     ),
        #     2,
        # )
        data["asset_price"] = round(float(data["net_weight"]) * gold_price, 2)
        data['asset_price_per_gram'] = gold_price
        return data

    def update_asset_details(self, data, asset):
        # if asset is None:
        #     application=self.__get_application_instance(application)
        if asset.application is None:
            return custom_response_obj(message='Application does not exist',
                                       code=404,
                                       error_msg='Application does not exist',
                                       error_code=404)
        application = asset.application
        ltv_percentage = application.product.ltv_percentage
        data=self.__create_payload(data, asset.application)
        ser = self.__get_serializer_instance(data,asset)
        if ser.is_valid():
            # print("net_weight:  ", net_weight)
            # print("karat_value:  ", karat_value)


            old_eligible_amount = round(
                float(asset.asset_price) * float(ltv_percentage) * 0.01, 2
            )

            # print("eligible_amount :  ",eligible_amount)
            # if Asset.objects.filter(application=application).count() == 0:
            #     application.eligible_amount = eligible_amount
            #     # if application.eligible_amount :
            #     #     print("previous eligible_amount : ",application.eligible_amount)
            #     #     application.eligible_amount=eligible_amount+application.eligible_amount
            #     # else :
            #     #
            # else:

            ## Deducting the old data
            application.eligible_amount -= old_eligible_amount
            application.net_weight -= asset.net_weight
            application.total_wastage -= asset.wastage
            application.total_gross_weight -= asset.gross_weight
            application.total_asset_price -= asset.asset_price


            ## Adding the new data
            new_asset_price = ser.validated_data["asset_price"]
            new_eligible_amount = round(
                float(new_asset_price) * float(ltv_percentage) * 0.01, 2
            )
            application.eligible_amount += new_eligible_amount
            application.net_weight += ser.validated_data["net_weight"]
            application.total_wastage += ser.validated_data["wastage"]
            application.total_gross_weight += ser.validated_data["gross_weight"]
            application.total_asset_price += new_asset_price

            # if asset is None:
            #     #application.status = APPLICATION_STATUS.ASSET_ADDED.value
            #     application.eligible_amount = (
            #             eligible_amount + application.eligible_amount
            #     )
            # else:

            # asset_amount = asset.asset_price
            # previous_amount = round(
            #     float(asset_amount) * float(ltv_percentage) * 0.01, 2
            # )
            # difference=eligible_amount-previous_amount
            # application.eligible_amount = (difference + application.eligible_amount)


            # if application.net_weight:
            #     application.net_weight = net_weight + application.net_weight
            # else:
            #     application.net_weight = net_weight
            application.save()
            ser.save()
            return custom_response_obj(message='Asset items updated successfully',
                                       code=200)
        return custom_response_obj(message=ser.errors,
                                   code=400,
                                   error_msg=ser.errors,
                                   error_code=400)

    def __get_serializer_instance(self, data,asset):
        if asset:
            return AssetSingleSerializer(asset, data=data, partial=True)
        else:
            return AssetSingleSerializer(data=data)


    def check_all_assets_uploaded(self, asset):
        all_uploaded_assets= list(asset.asset_document_asset.values_list('asset_document_type', flat=True).all())
        all_asset_docs =[i[0] for i in ASSET_DOCUMENT]
        result=False
        for i in all_uploaded_assets:
            if i in all_asset_docs:
                result=True
            else:
                result=False
        return result