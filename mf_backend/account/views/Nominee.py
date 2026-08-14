from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from application.models import Application
from lender.serializers import LenderSerializer
from loan.models import LoanTakeOver
from product.serializers import ProductCreateSerializer
from utils.constants import ACCOUNT_STATUS, APPLICATION_STATUS, ApplicationType , LOAN_TYPE , INSURANCE_APPLICABLE , PRODUCT_TYPE
from ..serializers import NomineeSerializer, AccountWithInsuranceSerializer, WellnessNomineeDetailsSerializer
from utils.responseHandler import HttpResponse
from ..models import Account, NomineeDetails
import traceback
from utils.envSetup import environment
from ..service.insurance_service import InsuranceService
from decimal import Decimal
from account.models import InsuranceProduct
from datetime import datetime
from django.utils.timezone import localtime
class NomineeDetailsView(APIView):
    # TODO: structure below code
    def get(self, request, *args, **kwargs):
        try:
            application_id=request.GET.get('application_id')
            if not application_id:
                return HttpResponse.BadRequest({'msg':'Application id is required'})
            application=Application.objects.get(application_id=application_id)
            product=application.product
            account= Account.objects.get(account_id=request.GET.get("account_id", ""))
            data=AccountWithInsuranceSerializer(account).data
            nominees=list(account.nomieedetails_account.all().values())
        
            for nominee in nominees:
                date_of_birth = nominee.get('date_of_birth')
                if date_of_birth:
                # Convert to local time or simply remove the time part
                    nominee['date_of_birth'] = date_of_birth.strftime('%Y-%m-%d')
                else:
                    # Handle case where date_of_birth is None
                    nominee['date_of_birth'] = None
            
            insurance_mandatory=False
            show_insurance_fields=True
            if application_id:
                if application.lender.lender_code=='FINCARE_SMALL_FINANCE_BANK':
                    show_insurance_fields=False
                if application.application_type=='NEW' or application.loan_amount is not None:
                    loan_amount = application.loan_amount
                else:
                    loan_amount=LoanTakeOver.objects.get(application__application_id=application.application_id).requested_amount_from_radian
                if loan_amount>30000 and application.lender.lender_code==environment.RADIAN_LENDER_CODE:
                    insurance_mandatory=True
            response={
                'nominee':nominees,
                'insurance':data,
                'insurance_mandatory':insurance_mandatory,
                'application':{
                    'application_id':application_id,
                    'application_type':application.application_type,
                    'product':ProductCreateSerializer(product).data,
                    'status': application.status
                },
                'lender':LenderSerializer(application.lender).data,
                'show_insurance_fields':show_insurance_fields
            }
            #serializer = NomineeSerializer(nominee_id)
            return HttpResponse.Success(response)
        except ObjectDoesNotExist:
            return HttpResponse.BadRequest({'msg':'requested data not found'})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            account_id = request.GET.get("account_id", "")
            application_id=request.data.get('application_id', None)
            account = Account.objects.get(account_id=account_id)
            if application_id:
                application=Application.objects.get(application_id=application_id)
            else:
                application=None
            print("payload",data)
            insurance_id = data.get('insurance_id', None)
            print(insurance_id)
            product = application.product
            if application:
                if application.application_type=='NEW' or application.loan_amount is not None:
                    loan_amount=application.loan_amount
                else:
                    loan_amount = LoanTakeOver.objects.get(application__application_id=application.application_id).requested_amount_from_radian
                if loan_amount > 30000 and application.lender.lender_code == environment.RADIAN_LENDER_CODE and not insurance_id:
                    return HttpResponse.Success({'msg': 'Insurance is mandatory for radian product'})
            data["account"] = account.account_id
            if product is not None and product.insurance_applicable_on == INSURANCE_APPLICABLE.ACCOUNT.value :
                data['insurance_policy_selected'] = insurance_id
            elif application.application_type==ApplicationType.TAKEOVER.value:
                data['insurance_policy_selected'] = insurance_id
            else:
                print("pass")
                pass
            serializer = NomineeSerializer(data=data)
            if serializer.is_valid():
                obj, created = NomineeDetails.objects.update_or_create(
                    account=account, defaults=serializer.validated_data
                )
                print("created: ")
                print(created)
                if application:
                    ####################################################
                    product = application.product 
                    if product is not None:
                    
                        # New logic for wellness product and insurance applicability
                        if product.insurance_applicable_on == INSURANCE_APPLICABLE.APPLICATION.value:
                            if not insurance_id:
                                return HttpResponse.Success({'msg': 'Insurance is mandatory for wellness product'})
                            
                    ####################################################
                    if application.application_type==ApplicationType.TAKEOVER.value and (application.status==APPLICATION_STATUS.TAKE_OVER_LOAN_INITIATED.value or application.status==APPLICATION_STATUS.BT_RESIDENCE_ADDED.value):
                        application.status=APPLICATION_STATUS.BT_NOMINEE_ADDED.value
                        application.save()
                    if created and account.status!=ACCOUNT_STATUS.ACCOUNT_CONFIRMED.value:
                        account.status=ACCOUNT_STATUS.NOMINEE_ADDED.value
                        account.save()
                    if insurance_id and application:
                        res=InsuranceService().assign_insurance_to_account_nominee(account,insurance_id, application)
                        print('insurance result', res)  
                resp = Response({"status": "success", "data": serializer.data})
                return resp
            resp = Response({"status": "error", "errors": serializer.errors})
            return resp
        except Application.DoesNotExist:
            return HttpResponse.Success(data={'msg':'Application id not found'})
        except NomineeDetails.DoesNotExist:
            return HttpResponse.Unauthorized("Invalid credentials given")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def patch(self, request):
        try:
            data = request.data
            # Age check
            if int(data["age"]) > 70:
                return HttpResponse.BadRequest({"message": "Age should be less than 70"})
            # Fetch nominee details
            nominee = NomineeDetails.objects.get(
                nominee_id=request.GET.get("nominee_id", "")
            )
            application_id = request.data.get('application_id', None)
            application = Application.objects.get(application_id=application_id)
            account = application.account
            insurance_id = data.get('insurance_id', None)
            # If insurance_id is null, skip insurance processing
            if insurance_id is not None:
                print("INSURANCE ID PROVIDED")
                insurance_deduction = Decimal(0)
                other_deduction_amount = Decimal(0)
                product = application.product
                # Case when application product is not None
                if product is not None:
                    print(product.insurance_applicable_on)
                    # Check if insurance is applicable on the account level
                    if product.insurance_applicable_on == INSURANCE_APPLICABLE.ACCOUNT.value:
                        if nominee.insurance_policy_selected is not None:
                            # Error message if insurance is already applied at the account level
                            return HttpResponse.BadRequest(
                                {"message": "Insurance has already been applied for this account."}
                            )
                        else:
                            # Set new insurance policy if no previous one exists
                            data['insurance_policy_selected'] = insurance_id
                    insurance = InsuranceProduct.objects.get(insurance_policy_id=insurance_id)
                    # Handle other deductions
                    if product.other_deduction:
                        for deduction in product.other_deduction:
                            if deduction.get('price'):
                                other_deduction_amount += Decimal(deduction['price'])
                            elif deduction.get('percentage'):
                                other_deduction_amount += Decimal((deduction['percentage'] / 100) * float(insurance.price))
                    print(f"Other Deduction Amount: {other_deduction_amount}")
                    insurance_deduction = insurance.price
                    if insurance :
                        application.insurance_product = insurance
                        application.insurance_amount_deducted = insurance_deduction
                    else:
                        application.insurance_product=account.insurance_product
                        # application.insurance_amount_deducted = account.insurance_amount
                    application.net_disbursed_amount = application.net_disbursed_amount - insurance_deduction - other_deduction_amount
                    application.save()
                    # Apply insurance to the account if not already applied
                    if product.insurance_applicable_on == INSURANCE_APPLICABLE.ACCOUNT.value:
                        if account.insurance_product is None:
                            account.insurance_product = insurance
                            account.insurance_amount =insurance.price
                            account.save()
            # Case when status is TAKE_OVER_LOAN_INITIATED and product is None
            elif application.application_type==ApplicationType.TAKEOVER.value and (application.status==APPLICATION_STATUS.TAKE_OVER_LOAN_INITIATED.value or application.status==APPLICATION_STATUS.BT_RESIDENCE_ADDED.value):
                    print("takeover")
                    
                    if insurance_id is not None:
                        data['insurance_policy_selected'] = insurance_id
                        insurance = InsuranceProduct.objects.get(insurance_policy_id=insurance_id)
                        print(f"Other Deduction Amount: {other_deduction_amount}")
                        insurance_deduction = insurance.price
                        if insurance :
                            application.insurance_product = insurance
                            application.insurance_amount_deducted = insurance.price
                            if account.insurance_product is None:
                                account.insurance_product = insurance
                                account.insurance_amount =insurance.price
                                account.save()
                    else:
                        application.insurance_product=account.insurance_product
                        # application.insurance_amount_deducted = account.insurance_amount
                    application.save()
                    if application.application_type==ApplicationType.TAKEOVER.value and (application.status==APPLICATION_STATUS.TAKE_OVER_LOAN_INITIATED.value or application.status==APPLICATION_STATUS.BT_RESIDENCE_ADDED.value):
                        application.status=APPLICATION_STATUS.BT_NOMINEE_ADDED.value
                        application.save()
            elif application.application_loan_type == LOAN_TYPE.WELLNESS.value:
                print("Processing WELLNESS loan type")
                print("NOMINEEACCOUNT:",nominee.date_of_birth)
                # Handle the logic for wellness loans, similar to the POST method
                dob = data.get('date_of_birth')
                print("DATA",dob)
                if dob:
                    # Ensure the timezone is correctly handled (without shifting dates)
                    dob = datetime.strptime(dob, "%Y-%m-%d")  # Maintain the date exactly as entered
                    age = InsuranceService().calculate_age(dob)
                    data["age"] = age
            else:
                print("ELSE")
                application.insurance_product=account.insurance_product
                # application.insurance_amount_deducted = account.insurance_amount
                application.save()
            # Update nominee details regardless of insurance
            serializer = NomineeSerializer(nominee, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"nominee": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except NomineeDetails.DoesNotExist as e:
            return HttpResponse.BadRequest({"error": str(e)})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError({"error": str(e)})

    
        

class WellnessNomineeView(APIView):
    def post(self, request):
        data = request.data
        account_id = request.GET.get("account_id", "")
        application_id = request.data.get('application_id', "")

        if not account_id or not application_id:
            return HttpResponse.BadRequest({"error": "Both account_id and application_id are required."})

        try:
            # Fetch account and application, handle exceptions for invalid objects
            account = Account.objects.get(account_id=account_id)
            application = Application.objects.get(application_id=application_id)

            # Check if the product type is WELLNESS
            if application.product.product_type != LOAN_TYPE.WELLNESS.value:
                return HttpResponse.BadRequest({"error": "The product must be of type 'WELLNESS'."})

            data.pop('application_id', None)

            # Add account ID to the data
            data["account"] = account

            # Extract date of birth and calculate age
            dob = data.get('date_of_birth')  # Make sure the request contains 'date_of_birth'
            if dob:
                dob = datetime.strptime(dob, "%Y-%m-%d")  # Assuming date format is YYYY-MM-DD
                age = InsuranceService().calculate_age(dob)
                data["age"] = age  # Save the calculated age in the data
            else:
                return HttpResponse.BadRequest({"error": "Date of birth is required."})

            # Check if a nominee already exists for this account
            nominee_details = NomineeDetails.objects.filter(account=account).first()

            if nominee_details:
                # Update existing nominee details
                for key, value in data.items():
                    setattr(nominee_details, key, value)
                nominee_details.save()
                created = False  # Set created to False since we're updating
            else:
                # Create a new nominee
                nominee_details = NomineeDetails.objects.create(**data)
                created = True  # Set created to True since we're creating

            # Process insurance and deductions
            product = application.product

            other_deduction_amount = Decimal(0)
            if product.other_deduction:
                for deduction in product.other_deduction:
                    if deduction.get('price'):
                        other_deduction_amount += Decimal(deduction['price'])
                    elif deduction.get('percentage'):
                        other_deduction_amount += Decimal(deduction['percentage'] / 100) 
            # Calculate total deduction
            insurance_deduction = other_deduction_amount
            application.insurance_amount_deducted = insurance_deduction
            application.net_disbursed_amount = other_deduction_amount
            application.loan_amount=0
            application.status = APPLICATION_STATUS.WELLNESS_NOMINEE_ADDED.value
            application.save()


            # Update account status
            account.status = ACCOUNT_STATUS.NOMINEE_ADDED.value
            account.save()

            # Return the saved nominee details
            return HttpResponse.Success({"nominee": WellnessNomineeDetailsSerializer(nominee_details).data, "created": created})

        except ObjectDoesNotExist as e:
            return HttpResponse.InternalServerError({"error": str(e)})

        except InsuranceProduct.DoesNotExist:
            return HttpResponse.InternalServerError({"error": "Invalid insurance ID provided."})

        except Exception as e:
            return HttpResponse.InternalServerError({"error": f"An error occurred: {str(e)}"})
        
        
            
   