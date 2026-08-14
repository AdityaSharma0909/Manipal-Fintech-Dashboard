from rest_framework.views import APIView
from application.serializers import ApplicationOverviewSerializer
from application.models import AssetDocuments
from document.utils.asset_document_utils import AssetDocumentUtils
from document.serializers import AssetDocumentSerializer
from utils.responseHandler import HttpResponse
from utility.response_handler import HttpResponse as response_handler
from asset.models import Asset
from application.models import Application
from disbursements.models import Disbursement
from disbursements.serializers import DisbursementSerializer
from disbursements.service.constants import DisbursalConstants
from branch.models import BranchUserMapping
from branch.serializers import CreateBranchSerializer
import traceback
from document.utils import asset_document_utils
from utils.helper import get_gold_price
from ..serializers import (
    AssetSerializer,
    AssetSingleSerializer,
    AssetSerializerModified,
)
from instance import SerilizerInstance
import utils.helper as helper
from utils.constants import APPLICATION_STATUS, ApplicationType, ASSET_DOCUMENT
from ..services.asset_service import AssetService
from utils.envSetup import environment


class AssetView(APIView):
    def post(self, request, *args, **kwargs):
        try:

            data = request.data
            application = Application.objects.get(
                application_id=request.GET.get("application_id", "")
            )
            # print(data)
            total_assets = Asset.objects.filter(application=application)
            if len(total_assets) >= 10:
                return HttpResponse.Success(
                    {"msg": "Limit reached, only 10 assets are allowed"}
                )
            data["gross_weight"] = float(data["gross_weight"])
            data["net_weight"] = float(data["net_weight"])
            data["karat_value"] = int(data["karat_value"])
            data["application"] = str(application)
            data["leverage"] = 3
            # gold_price = helper.price_of_gold_22_karates()

            gold_price = get_gold_price(lender=application.lender, karat=data["karat_value"])

            # # TODO need to remove below hard coded logic that 100 rs will be added to gold price for own book(Radian) products
            # if application.product.lender.lender_code == environment.RADIAN_LENDER_CODE:
            #     gold_price = gold_price + 100

            # price_of_22_karate = gold_price
            # price_of_22_karate = float(price_of_22_karate["gold_price__avg"])
            data["marketvalueatappraisal"] = gold_price
            # data["net_weight_22k"] = round(
            #     helper.customer_gold_weight_converter_to_22_karate_weight(
            #         data["karat_value"], data["net_weight"]
            #     ),
            #     2,
            # )
            data["asset_price"] = float(round(float(data["net_weight"]) * gold_price))

            # data["asset_price"] = round(float(
            #     int(
            #         helper.gold_asset_price(data["karat_value"], data["net_weight"])
            #         * 100
            #     )
            #     / 100
            # ),2)
            ltv_percentage = application.product.ltv_percentage
            data["asset_price_per_gram"] = gold_price
            ser = AssetSingleSerializer(data=data)
            if ser.is_valid():
                # net_weight = ser.validated_data["net_weight"]
                asset_price = ser.validated_data["asset_price"]
                # print("net_weight:  ", net_weight)
                # print("karat_value:  ", karat_value)

                # application.status = APPLICATION_STATUS.ASSET_ADDED.value

                eligible_amount = round(
                    float(asset_price) * float(ltv_percentage) * 0.01, 2
                )

                # print("eligible_amount :  ",eligible_amount)
                if len(total_assets) == 0:
                    application.eligible_amount = eligible_amount
                    application.net_weight = ser.validated_data["net_weight"]
                    application.total_wastage = ser.validated_data["wastage"]
                    application.total_gross_weight = ser.validated_data["gross_weight"]
                    application.total_asset_price = ser.validated_data["asset_price"]
                else:
                    # if application.eligible_amount:
                    application.eligible_amount += eligible_amount
                    application.net_weight += ser.validated_data["net_weight"]
                    application.total_wastage += ser.validated_data["wastage"]
                    application.total_gross_weight += ser.validated_data["gross_weight"]
                    application.total_asset_price += ser.validated_data["asset_price"]
                    # else:
                    #     application.eligible_amount = eligible_amount
                # if application.net_weight:
                #     application.net_weight = net_weight + application.net_weight
                # else:
                #     application.net_weight = net_weight

                ser.save()

                application.save()
                return HttpResponse.Success({"asset": ser.data})
            return HttpResponse.BadRequest({"error": ser.errors})

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def delete(self, request):
        try:

            asset = Asset.objects.get(asset_id=request.query_params.get("asset_id"))
            # assets = Asset.objects.filter(application=asset[0].application)
            # if len(assets) == 1:
            #     eligible_amount = 0
            #     application.net_weight = 0
            #     application.processing_fee = 0
            #     application.gst = 0
            #     application.disbursal_amount = 0
            #     application.net_disbursed_amount = 0

            # else:

            application = asset.application
            ltv_percentage = application.product.ltv_percentage

            # eligible_amount = helper.gold_karat_converter(
            #     customer_gold_karate=int(asset.karat_value),
            #     total_num_of_gold_in_grams=int(asset.net_weight),
            #     ltv_percentage=ltv_percentage,
            # )

            eligible_amount = (asset.asset_price * ltv_percentage) / 100
            application.eligible_amount -= eligible_amount
            application.net_weight -= asset.net_weight
            application.total_wastage -= asset.wastage
            application.total_gross_weight -= asset.gross_weight
            application.total_asset_price -= asset.asset_price
            application.save()

            asset.delete()
            return HttpResponse.Success({"data": "Sucessfully deleted"})
        except Asset.DoesNotExist as ae:
            return HttpResponse.BadRequest(str(ae))
        except Exception as err:
            return HttpResponse.InternalServerError(str(err))

    def patch(self, request, *args, **kwargs):
        try:
            data = request.data

            asset_id = data.get("asset_id")
            asset = Asset.objects.get(asset_id=asset_id)
            response = AssetService().update_asset_details(data=data, asset=asset)
            resp = response_handler().response(
                code=response.get("status_code"),
                data=response.get("message"),
                error_code=response.get("error_code", None),
                error_msg=response.get("error_msg"),
            )
            return resp
        except Asset.DoesNotExist as e:
            return HttpResponse.BadRequest("asset does not exist")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class AssetDocumentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            asset = Asset.objects.get(asset_id=request.query_params.get("asset_id"))

            application = asset.application
            try:
                asset_doc = AssetDocuments.objects.get(
                    asset__asset_id=asset.asset_id,
                    asset_document_type=request.data.get("asset_document_type"),
                )
                asset_doc.delete()
            except Exception as e:
                pass
            document_serialized = AssetDocumentUtils(request.user).upload_document_new(
                file=request.data.get("file"),
                document_type=request.data.get("asset_document_type"),
                application=str(asset.application.application_id),
                asset=str(asset.asset_id),
            )

            if document_serialized.is_valid():
                document_serialized.save()
                all_assets_uploaded = AssetService().check_all_assets_uploaded(asset)
                if all_assets_uploaded:
                    application.status = APPLICATION_STATUS.ASSET_ADDED.value
                    application.save()
                resp = HttpResponse.Success({"asset": document_serialized.data})
                return resp
            resp = HttpResponse.BadRequest({"errors": document_serialized.errors})
            return resp
        except AssetDocuments.DoesNotExist as e:
            return HttpResponse.BadRequest("Invalid Asset document")
        except AssetDocuments.DoesNotExist as e:
            return HttpResponse.Unauthorized("Invalid credentials given")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    # get documents by application_id
    def get(self, request):
        try:
            application = Application.objects.get(
                application_id=request.GET.get("application_id", "")
            )
            if not application:
                return HttpResponse.BadRequest("Invalid application_id")

            assets = Asset.objects.filter(application=application)

            ass_ser = AssetSerializerModified(assets, many=True)
            app_ser = ApplicationOverviewSerializer(application)
            # print("ass_ser ", ass_ser.data)

            disbursment_txn = []
            if application.application_type == ApplicationType.TAKEOVER.value:
                disbursments = Disbursement.objects.filter(
                    application=application,
                    disbursement_status=DisbursalConstants.TAKEOVER.value,
                )
                disbursment_txn = DisbursementSerializer(disbursments, many=True).data
            app = {
                "total_asset_price": app_ser.data["total_asset_price"],
                "total_eligble_amount": float(app_ser.data["eligible_amount"]) if app_ser.data["eligible_amount"] is not None else None,
                # "total_net_weight": app_ser.data["total_net_weight"],
                # "total_net_weight_in_22k": app_ser.data["total_net_weight_in_22k"],
                "total_wastage": app_ser.data["total_wastage"],
                "total_gross_weight": app_ser.data["total_gross_weight"],
                "eligible_amount": app_ser.data["eligible_amount"],
                # "total_weight": app_ser.data["total_weight"],
                "net_weight": app_ser.data["net_weight"],
                "period": app_ser.data["period"],
                "processing_fee": app_ser.data["processing_fee"],
                "current_gst_rate": app_ser.data["current_gst_rate"],
                "gst": app_ser.data["gst"],
                "stamp_duty": app_ser.data["stamp_duty"],
                "penalty": app_ser.data["penalty"],
                "ltv": app_ser.data["ltv"],
                "gold_rate_per_gram": app_ser.data["gold_rate_per_gram"],
                "lending_gold_rate_per_gram": app_ser.data[
                    "lending_gold_rate_per_gram"
                ],
                "tenure": app_ser.data["tenure"],
                "intrest_rate": app_ser.data["intrest_rate"],
                "disbursment_txn": disbursment_txn,
            }
            if app_ser.data["product"] is not None:
                app["processing_fee_percent"] = app_ser.data["product"][
                    "processing_fee"
                ]
                app["maximum_ticket_size"] = app_ser.data["product"][
                    "maximum_ticket_size"
                ]
                app["minimum_ticket_size"] = app_ser.data["product"][
                    "minimum_ticket_size"
                ]
                app["product_category"] = app_ser.data["product"]["product_category"]

            branch = BranchUserMapping.objects.get(user=application.Originatedby).branch
            return HttpResponse.Success(
                {
                    "assets": ass_ser.data,
                    "application": app,
                    "branch": CreateBranchSerializer(branch).data,
                }
            )
        except BranchUserMapping.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except AssetDocuments.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
