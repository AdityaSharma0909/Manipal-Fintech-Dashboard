from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import utils.helper as helper
import traceback
from product.models import Product
from utils.responseHandler import HttpResponse
from datetime import datetime
from product.serializers import ProductCreateSerializer
import traceback
from lead.models import Lead
from lead.serializers import OpenLeadSerializer
from users.models import VerificationToken
from django.utils import timezone
from asset.serializers import GoldPriceSerializer
from utils.helper import get_radian_gold_price_by_karat, get_radian_gold_price_obj
from utils.envSetup import environment
from asset.models import GoldPriceData
from utils.envSetup import environment


class CheckUpdateView(APIView):
    permission_classes = (AllowAny,)
    LATEST_VERSION = "1.0.20"

    def post(self, request):
        try:
            client_version = request.data.get("current_app_version", None)
            if not client_version:
                return HttpResponse.BadRequest("current_app_version is required")

            def version_to_int(v):
                return int(str(v).replace(".", ""))

            try:
                client_val = version_to_int(client_version)
                latest_val = version_to_int(self.LATEST_VERSION)
            except ValueError:
                return HttpResponse.BadRequest("Invalid version format")

            update_available = client_val > latest_val

            return HttpResponse.Success(
                {
                    "status": update_available,
                    "latest_version": self.LATEST_VERSION,
                }
            )
        except Exception as err:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(err))


class GoldValue(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            karat = int(request.GET.get("karat", "22"))

            gold_price = GoldPriceData.objects.get(
                karat=karat, lender__lender_code=environment.RADIAN_LENDER_CODE
            ).gold_price
            print(gold_price)

            return HttpResponse.Success(
                {
                    "gold_price": gold_price,
                    "karat": karat,
                    "date": datetime.now(),
                }
            )
        except GoldPriceData.DoesNotExist as gpd:
            return HttpResponse.BadRequest(str(gpd))
        except Exception as err:
            return HttpResponse.InternalServerError(str(err))


class GoldPricesView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            goldPrices = get_radian_gold_price_obj()
            resp = GoldPriceSerializer(goldPrices, many=True).data
            return HttpResponse.Success({"gold_prices": resp})
        except Exception as err:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(err))


class LoanCalculatorByAmount(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            loan_amount = float(request.GET.get("loan_amount", ""))
            karat = request.GET.get("karat", None)
            if karat is None:
                karat = 22
            elif karat.isdigit():
                karat = int(karat)
                if karat < 18 or karat > 22:
                    return HttpResponse.BadRequest(
                        "Enter valid karat between 18 to 20."
                    )
            else:
                return HttpResponse.BadRequest("Enter valid karat between 18 to 20.")

            gold_price = get_radian_gold_price_by_karat(karat=karat)

            asset_amount = (loan_amount * 75) / 100

            gold_required_in_gm = float(asset_amount) / float(gold_price)

            return HttpResponse.Success(
                {
                    "gold_in_gms": gold_required_in_gm,
                    "loan_amount": loan_amount,
                    "date": datetime.now(),
                }
            )
            # price=loan_amount+(100-product.ltv_percentage)*loan_amount/100
            # return HttpResponse.Success(price/(t.get_gold_price()/10))
        except Exception as err:
            return traceback.print_exc()


class LoanCalculatorByAsset(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            gold_in_gm = float(request.GET.get("gold_in_gm", ""))
            karat = request.GET.get("karat", None)
            if karat is None:
                karat = 22
            elif karat.isdigit():
                karat = int(karat)
                if karat < 18 or karat > 22:
                    return HttpResponse.BadRequest(
                        "Enter valid karat between 18 to 20."
                    )
            else:
                return HttpResponse.BadRequest("Enter valid karat between 18 to 20.")

            # product = Product.objects.get(product_id=request.GET.get("product_id", ""))
            # gold_price = GoldPriceData.objects.get(karat=22).gold_price
            gold_price = get_radian_gold_price_by_karat(karat=karat)
            loan_amount = gold_in_gm * float(gold_price) * 0.75

            return HttpResponse.Success(
                {
                    "gold_in_gms": gold_in_gm,
                    "loan_amount": loan_amount,
                    "date": datetime.now(),
                }
            )

        except Exception as err:
            return traceback.print_exc()


class RadianProductView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            product = Product.objects.filter(
                lender__lender_code=environment.RADIAN_LENDER_CODE
            )
            return HttpResponse.Success(
                {"products": ProductCreateSerializer(product, many=True).data}
            )

        except Exception as err:
            traceback.print_exc()
            return HttpResponse.InternalServerError("Something went wrong...")


class GenerateOpenLeadsView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            phone = request.data.get("phone", None)
            leads = Lead.objects.filter(phone=phone)
            if len(leads) > 0:
                # leads[0].update(**serializer.validated_data)
                serializer = OpenLeadSerializer(leads[0], data=request.data)
            else:
                serializer = OpenLeadSerializer(data=request.data)

            if serializer.is_valid():
                vt = VerificationToken.objects.get(
                    token=serializer.validated_data["verification_token"],
                    identification=serializer.validated_data["phone"],
                )
                if timezone.now() < vt.expiry:
                    serializer.save()
                    resp = HttpResponse.Success({"lead": serializer.data})
                    return resp
                else:
                    return HttpResponse.BadRequest("verification_token is expired")

            return HttpResponse.BadRequest(serializer.errors)
        except VerificationToken.DoesNotExist as vd:
            # return HttpResponse.InternalServerError(str(vd))
            return HttpResponse.Forbidden("Please verify your mobile number to proceed.")
        except Exception as err:
            traceback.print_exc()
            return HttpResponse.InternalServerError("Something went wrong...")


class LegalDocumentsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            base_url = request.build_absolute_uri('/')[:-1]
            return HttpResponse.Success({
                "terms_of_use": {
                    "html": f"{base_url}/static_assets/fincome_terms_of_use.html",
                    "docx": f"{base_url}/static_assets/fincome_terms_of_use.docx"
                },
                "privacy_policy": {
                    "html": f"{base_url}/static_assets/fincome_privacy_policy.html",
                    "docx": f"{base_url}/static_assets/fincome_privacy_policy.docx"
                }
            })
        except Exception as err:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(err))
