from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from utils.responseHandler import HttpResponse
from utils.constants import ROLES, SALES_PAYOUT_TYPE
from payment.models import SalesOfficerPayout
from payment.serializers import SalesOfficerPayoutSerializer
from onboarding_v2.constants import LeadSource
from onboarding_v2.models import ApplicationV2, LeadV2
from account.models import Account, AgentAccount, AgentBankAccount
import traceback
import pandas as pd
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum
from utils import helper
from asset.models import GoldPriceHistory
from utils.envSetup import environment

class SalesOfficerCommissionListView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            payout_type = SALES_PAYOUT_TYPE.COMMISSION.value
            if user.role == ROLES.SALES_OFFICER.value:
                queryset = SalesOfficerPayout.objects.filter(so_user=user, payout_type=payout_type)
            elif user.role in [ROLES.CPC.value, ROLES.SUPER_ADMIN.value, ROLES.VERTICAL_ADMIN.value]:
                queryset = SalesOfficerPayout.objects.filter(payout_type=payout_type)
            else:
                return HttpResponse.Forbidden({"error": "Not Allowed"})
            queryset = queryset.order_by("-created_at")
            try:
                page = int(request.GET.get("page", 1))
            except (TypeError, ValueError):
                page = 1
            try:
                page_size = int(request.GET.get("page_size", 20))
            except (TypeError, ValueError):
                page_size = 20
            page_size = max(1, min(page_size, 100))
            paginator = Paginator(queryset, page_size)
            try:
                page_obj = paginator.page(page)
            except (EmptyPage, PageNotAnInteger):
                page_obj = paginator.page(paginator.num_pages)
            serializer = SalesOfficerPayoutSerializer(page_obj.object_list, many=True)
            return HttpResponse.Success({
                "payouts": serializer.data,
                "count": paginator.count,
                "page": page_obj.number,
                "page_size": page_size,
                "num_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "next": page_obj.number + 1 if page_obj.has_next() else None,
                "previous": page_obj.number - 1 if page_obj.has_previous() else None
            })
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class SalesOfficerIncentiveListView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            payout_type = SALES_PAYOUT_TYPE.INCENTIVE.value
            if user.role == ROLES.SALES_OFFICER.value:
                queryset = SalesOfficerPayout.objects.filter(so_user=user, payout_type=payout_type)
            elif user.role in [ROLES.CPC.value, ROLES.SUPER_ADMIN.value, ROLES.VERTICAL_ADMIN.value]:
                queryset = SalesOfficerPayout.objects.filter(payout_type=payout_type)
            else:
                return HttpResponse.Forbidden({"error": "Not Allowed"})
            queryset = queryset.order_by("-created_at")
            try:
                page = int(request.GET.get("page", 1))
            except (TypeError, ValueError):
                page = 1
            try:
                page_size = int(request.GET.get("page_size", 20))
            except (TypeError, ValueError):
                page_size = 20
            page_size = max(1, min(page_size, 100))
            paginator = Paginator(queryset, page_size)
            try:
                page_obj = paginator.page(page)
            except (EmptyPage, PageNotAnInteger):
                page_obj = paginator.page(paginator.num_pages)
            serializer = SalesOfficerPayoutSerializer(page_obj.object_list, many=True)
            return HttpResponse.Success({
                "payouts": serializer.data,
                "count": paginator.count,
                "page": page_obj.number,
                "page_size": page_size,
                "num_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "next": page_obj.number + 1 if page_obj.has_next() else None,
                "previous": page_obj.number - 1 if page_obj.has_previous() else None
            })
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class SalesOfficerPayoutUploadView(APIView):
    permission_classes = []

    def post(self, request, upload_type):
        try:
            user = request.user
            if user.role not in [ROLES.SALES_OFFICER.value, ROLES.CPC.value, ROLES.SUPER_ADMIN.value, ROLES.VERTICAL_ADMIN.value, ROLES.AGENT.value]:
                return HttpResponse.Forbidden({"error": "Not Allowed"})

            file_obj = request.FILES.get("file")
            if not file_obj:
                return HttpResponse.BadRequest({"error": "file is required"})

            payout_type = SALES_PAYOUT_TYPE.COMMISSION.value if upload_type == "commission" else SALES_PAYOUT_TYPE.INCENTIVE.value

            def normalize_header(col):
                return re.sub(r"[^a-z0-9]+", "_", str(col).strip().lower()).strip("_")

            def pick_sheet(xls, typ):
                sheet_candidates = {
                    "commission": [
                        "commission_agent",
                        "commission__agent",
                        "commissionagent",
                    ],
                    "incentive": [
                        "incentive_for_so",
                        "incentive_for_sales_officer",
                        "incentiveforso",
                        "incentive",
                    ],
                }
                norm_names = {normalize_header(n): n for n in xls.sheet_names}
                desired = sheet_candidates.get(typ, [])
                for cand in desired:
                    if cand in norm_names:
                        return norm_names[cand]
                return xls.sheet_names[0]

            name = getattr(file_obj, "name", "").lower()
            if name.endswith(".csv"):
                df = pd.read_csv(file_obj)
            else:
                xls = pd.ExcelFile(file_obj)

                df = pd.read_excel(xls, sheet_name=pick_sheet(xls, "commission" if payout_type == SALES_PAYOUT_TYPE.COMMISSION.value else "incentive"))

            df.columns = [normalize_header(c) for c in df.columns]
            def parse_date(val):
                try:
                    return pd.to_datetime(val)
                except Exception:
                    return None

            def get_val(row, keys):
                for k in keys:
                    v = row.get(k)
                    if v is None:
                        continue
                    try:
                        if pd.isna(v):
                            continue
                    except Exception:
                        pass
                    if str(v).strip() == "":
                        continue
                    return v
                return None

            def get_so_user_from_row(row):
                so_id = get_val(row, ["so_id"])
                if not so_id:
                    raise ValueError("SO ID is required")
                from django.contrib.auth import get_user_model
                so = get_user_model().objects.filter(employee_id=str(so_id).strip(), role=ROLES.SALES_OFFICER.value).first()
                if not so:
                    raise ValueError("SO ID not found")
                return so

            def get_agent_user_from_row(row):
                agent_id = get_val(row, ["agent_dsa_id", "agent_id", "agent_user_id"])
                if not agent_id:
                    raise ValueError("Agent/DSA ID is required")
                from django.contrib.auth import get_user_model
                agent = get_user_model().objects.filter(employee_id=str(agent_id).strip(), role=ROLES.AGENT.value).first()
                if not agent:
                    raise ValueError("Agent user_id not found or not AGENT")
                return agent

            def get_customer_from_row(row):
                app_num = get_val(row, ["customer_id", "cusstomer_id"])
                if not app_num:
                    raise ValueError("Customer ID is required")
                try:
                    return ApplicationV2.objects.get(application_id=str(app_num).strip())
                except Exception:
                    raise ValueError("Customer not found")

            def validate_customer(row):
                cust_id = get_val(row, ["cusstomer_id", "customer_id"])
                if cust_id:
                    acc = Account.objects.filter(customer_id=str(cust_id).strip()).first()
                    if not acc:
                        raise ValueError("Customer ID not found")
                    return str(cust_id).strip()
                return None

            created = 0
            errors = []

            for idx, row in df.iterrows():
                try:
                    so_user = get_so_user_from_row(row)
                    customer = get_customer_from_row(row)
                    # customer_external_id = validate_customer(row)

                    amount_field = "commission_amt" if payout_type == SALES_PAYOUT_TYPE.COMMISSION.value else "so_incentive"
                    amt = get_val(row, [amount_field])
                    if amt in [None, ""]:
                        continue

                    agent_name = get_val(row, ["agent_dsa_name_agent_type", "agent_dsa_name", "agent_name"])
                    agent_type = get_val(row, ["user_type", "agent_type"])
                    agent_external_id = None
                    if payout_type == SALES_PAYOUT_TYPE.COMMISSION.value:
                        agent = get_agent_user_from_row(row)

                        agent_external_id = str(agent.user_id) 

                    payload = {
                        "so_user": str(so_user.user_id),
                        "payout_type": payout_type,
                        "loan_id": str(get_val(row, ["loan_id_application_id"]) or ""),
                        "customer_name": row.get("customer_name"),
                        "customer_id": customer.application_id or str(get_val(row, ["customer_id"]) or ""),
                        "pincode": str(get_val(row, ["customer_pincode", "pin_code"]) or "") or "0",
                        "lead_id": str(get_val(row, ["lead_id"]) or ""),
                        "agent_name": agent_name,
                        "agent_user": agent_external_id,
                        "agent_type": str(agent_type or ""),
                        "request_amount": get_val(row, ["request_amt"]),
                        "disbursed_amount": get_val(row, ["disbursement_amount", "disbursed_amt"]),
                        "disbursed_on": parse_date(get_val(row, ["disbursement_date", "disbursed_on"])),
                        "status": str(get_val(row, ["status"]) or ""),
                        "utr": str(get_val(row, ["utr"]) or ""),
                        "amount": amt,
                        "clawback_amount": get_val(row, ["clawback_amt"]) or 0,
                        "settled_on": parse_date(get_val(row, ["settlement_date", "settled_on"])),
                        "settlement_amount": get_val(row, ["settlement_amt"]),
                        "created_by": str(user.user_id),
                        "modified_by": str(user.user_id),
                    }
                    check_loan_id = str(payload.get("loan_id", "")).strip()
                    if check_loan_id:
                        if SalesOfficerPayout.objects.filter(customer_id=customer.application_id, payout_type=payout_type).exists():
                            raise ValueError("Duplicate data: payout already exists for this customer_id and payout_type")
                    serializer = SalesOfficerPayoutSerializer(data=payload)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    created += 1
                except Exception as e:
                    errors.append({"row": idx + 2, "error": str(e)})

            if len(errors) > 0:
                return HttpResponse.BadRequest("Upload contains errors", data={"created": created, "errors": errors})
            return HttpResponse.Success({"created": created, "errors": errors})

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class AgentDashboardView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            if user.role not in [ROLES.AGENT.value, ROLES.CPC.value, ROLES.SUPER_ADMIN.value, ROLES.VERTICAL_ADMIN.value]:
                return HttpResponse.Forbidden({"error": "Not Allowed"})

            agent_user = user if user.role == ROLES.AGENT.value else None

            if agent_user is None:
                agent_user_id = request.GET.get("agent_user_id")
                if agent_user_id:
                    from users.models import User as U
                    try:
                        agent_user = U.objects.get(user_id=agent_user_id, role=ROLES.AGENT.value)
                    except Exception:
                        return HttpResponse.BadRequest({"error": "Invalid agent_user_id"})

            qs = SalesOfficerPayout.objects.filter(payout_type=SALES_PAYOUT_TYPE.COMMISSION.value)
            if agent_user is not None:
                qs = qs.filter(agent_user=agent_user)

            agg = qs.aggregate(sum_amount=Sum("amount"), sum_claw=Sum("clawback_amount"))
            sum_amount = float(agg.get("sum_amount") or 0)
            sum_claw = float(agg.get("sum_claw") or 0)
            commission_total = round(sum_amount - sum_claw, 2)

            lead_qs = LeadV2.objects.filter(source=LeadSource.AGENT)
            if agent_user is not None:
                lead_qs = lead_qs.filter(Q(created_by=agent_user) | Q(assigned_to=agent_user))
            total_leads = lead_qs.count()

            till_date = timezone.localdate().strftime("%d-%m-%Y")

            todays_price = helper.get_radian_gold_price_by_karat(karat=22)
            hist = (
                GoldPriceHistory.objects.values("gold_price")
                .filter(karat=22, lender__lender_code=environment.RADIAN_LENDER_CODE)
                .order_by("-created_at")
                .first()
            )
            yesterdays_price = float(hist["gold_price"]) if hist else todays_price

            dashboard_user = agent_user or user
            agent_profile = (
                AgentAccount.objects.filter(user=dashboard_user)
                .order_by("-created_at", "-modified_at")
                .first()
            )
            user_full_name = agent_profile.full_name if agent_profile else dashboard_user.get_full_name()
            agent_bank_account = (
                AgentBankAccount.objects.filter(agent=agent_profile).first()
                if agent_profile
                else None
            )
            bank_account_added = agent_bank_account is not None

            resp = {
                "user_full_name": user_full_name,
                "pincode": dashboard_user.pincode,
                "bank_status": "ADDED" if bank_account_added else "PENDING",
                "bank_account_added": bank_account_added,
                "bank_account_verified": bool(agent_bank_account and agent_bank_account.verified),
                "total_leads": total_leads,
                "commission": {
                    "till_date": till_date,
                    "amount": str(commission_total),
                },
                "total_earnings": str(commission_total),
                "gold": {
                    "todays_price_per_gram": str(round(float(todays_price or 0), 2)),
                    "yesterday_price_per_gram": str(round(float(yesterdays_price or 0), 2)),
                },
            }

            return HttpResponse.Success(resp)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
