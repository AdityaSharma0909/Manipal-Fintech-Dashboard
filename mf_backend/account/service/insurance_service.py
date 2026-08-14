import traceback

from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q
from datetime import datetime

from account.models import InsuranceProduct
from account.serializers import InsuranceSerializer
from application.models import Application
from instance import custom_response_obj
from utility.crud_helper import CrudHelper
from utils.constants import APPLICATION_STATUS , LOAN_TYPE , LENDING_TYPE , ApplicationType, INSURANCE_APPLICABLE


class InsuranceService:

    insurance_serializer=InsuranceSerializer
    insurance_crud=CrudHelper(insurance_serializer)

    def create_obj(self, data):
        add_obj=self.insurance_crud.add_obj(data=data)
        return add_obj

    # def get_all_insurance(self):
    #     get_data=self.insurance_crud.get_all_data()
    #     return {'status':200, 'data':{'insurance_product':get_data.get('data')}}

    def get_all_insurance(self, application_id=None):
        # Default filter for GOLD_LOAN type
        insurance_type = LENDING_TYPE.GOLD_LOAN.value
        tenure = None

        # Check application type and set filters accordingly
        if application_id:
            application = Application.objects.get(application_id=application_id)

            if application.application_loan_type == LENDING_TYPE.MSME_UNSECURED.value:
                insurance_type = LENDING_TYPE.MSME_UNSECURED.value
                tenure = application.product.tenure
                # Filter by MSME_UNSECURED type and matching tenure
                filters = Q(insurance_policy_type=insurance_type) & Q(tenure=tenure)

            elif application.application_loan_type == LENDING_TYPE.MSME_UNSECURED_AGRI.value:
                insurance_type = LENDING_TYPE.MSME_UNSECURED_AGRI.value
                tenure = application.product.tenure
                # Filter by MSME_UNSECURED type and matching tenure
                filters = Q(insurance_policy_type=insurance_type) & Q(tenure=tenure)

            elif application.application_loan_type == LENDING_TYPE.GOLD_LOAN.value:
                insurance_type = LENDING_TYPE.GOLD_LOAN.value

                if application.application_type == ApplicationType.TAKEOVER.value:
                    # When application type is TAKEOVER, filter by GOLD_LOAN type and product is null
                    filters = Q(insurance_policy_type=insurance_type) & Q(product__isnull=True)
                
                elif application.application_type == ApplicationType.NEW.value:
                    product = application.product
                    # Check if there's an insurance with the same product
                    if InsuranceProduct.objects.filter(insurance_policy_type=insurance_type, product=product).exists():
                        filters = Q(insurance_policy_type=insurance_type) & Q(product=product)
                    else:
                        # If no matching product, return insurance with GOLD_LOAN type and product is null
                        filters = Q(insurance_policy_type=insurance_type) & Q(product__isnull=True)
            
        else:
            # Filter by GOLD_LOAN type
            filters = Q(insurance_policy_type=insurance_type) & Q(product__isnull=True)

        # Fetch filtered insurance data
        get_data = self.insurance_crud.get_all_data(query=filters)
        return {'status': 200, 'data': {'insurance_product': get_data.get('data')}}



    def assign_insurance_to_account_nominee(self, account, insurance_id,application):
        try:
            print('account',account)
            insurance=InsuranceProduct.objects.get(insurance_policy_id=insurance_id)
            print('insurance policy,',insurance)

            # account.insurance_product=insurance
            # account.insurance_amount=insurance.price
            # print('account insurance=====>', account.insurance_product)
            # account.save()

            self.deduct_insurance_amount_from(application=application, insurance=insurance)
        except ObjectDoesNotExist:
            traceback.print_exc()
            return custom_response_obj(message={'msg':'data not found with given account and insurance id'},
                                       code=200)
        except Exception as e:
            traceback.print_exc()

    # def deduct_insurance_amount_from(self, application, source='nominee_add', insurance=None):
    #     try:
    #         if application.application_loan_type == LOAN_TYPE.GOLD_LOAN.value:
    #             account = application.account
    #             print(insurance)
    #             insurance = insurance if insurance is not None else account.insurance_product
    #             #print('insurance selected=====>', insurance, insurance.price,account.insurance_amount_covered_from.insurance_amount_deducted)
    #             insurance_deduction = 0
    #             save_account=False
    #             product = application.product
    #             other_deduction_amount = Decimal(0)

    #             if product.other_deduction:
    #                 for deduction in product.other_deduction:
    #                     if deduction.get('price'):
    #                         other_deduction_amount += Decimal(deduction['price'])
    #                     elif deduction.get('percentage'):
    #                         other_deduction_amount += Decimal((deduction['percentage'] / 100) * float(insurance.price))

                
    #             print(other_deduction_amount)
    #             # Case 1: Insurance product matches the application's product
    #             if insurance.product == application.product:
    #                 insurance_deduction = insurance.price
    #             else:
    #                 # if insurance:
    #                 # case-1 if insurance is deducted first time
    #                 print(account.insurance_amount_covered_from)
    #                 if account.insurance_amount_covered_from is None:
    #                     print("case 1")
    #                     insurance_deduction = insurance.price
    #                 #case -2
    #                 elif account.insurance_amount_covered_from and account.insurance_amount_covered_from.status==APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value:
    #                     print("case 2")
    #                     insurance_deduction=0
    #                     account.insurance_amount_covered_from=application
    #                     save_account=True
    #                 # case -3 if insurance has already been deducted but cutomer chose insurance with more benefits and more premium then deduct only the difference
    #                 elif account.insurance_amount_covered_from.insurance_amount_deducted != insurance.price:
    #                     print("case 3",account.insurance_amount_covered_from.insurance_amount_deducted,insurance.price)
    #                     insurance_deduction = abs(insurance.price - account.insurance_amount_covered_from.insurance_amount_deducted)

    #                 # case -4 if insurance is already taken and unchanged
    #                 elif application.application_type!="TAKEOVER" and account.insurance_amount_covered_from.insurance_amount_deducted == account.insurance_amount:
    #                     print("case 4")
    #                     insurance_deduction = 0


    #             if source=='nominee_add' and insurance_deduction>0:
    #                 application.insurance_product=insurance
    #                 application.insurance_amount_deducted = insurance_deduction
    #                 application.save()
    #                 account.insurance_product=insurance
    #                 account.insurance_amount=insurance.price
    #                 print('account insurance=====>', account.insurance_product)
    #                 account.save()
    #             #in case of takeover, net disbursed is done in loan amount addition screen in case of New it is done before collecting loan docs
    #             if application.application_type!="TAKEOVER" and source=='nominee_add' and insurance_deduction >0:
    #                 application.net_disbursed_amount = application.net_disbursed_amount - insurance_deduction - other_deduction_amount
    #                 application.insurance_product=insurance
    #                 application.save()

    #             print(source, account)
    #             if source=='marking_paid':
    #                 save_account=True
    #                 account.insurance_amount_covered_from=application
    #             if save_account:
    #                 account.save()
    #         elif application.application_loan_type == LOAN_TYPE.MSME_UNSECURED.value:
    #             application.insurance_product=insurance
    #             application.save()

    #         else:
    #             print("application type is msme unsecured")
    #             None
    #     except Exception as e:
    #         traceback.print_exc()


    def deduct_insurance_amount_from(self, application, source='nominee_add', insurance=None):
        try:
            account = application.account
            product = application.product
            other_deduction_amount = Decimal(0)
            save_account = False

            # Calculate other deductions (centralized logic for all loan types)
            if product.other_deduction:
                for deduction in product.other_deduction:
                    if deduction.get('price'):
                        other_deduction_amount += Decimal(deduction['price'])
                    elif deduction.get('percentage'):
                        other_deduction_amount += Decimal((deduction['percentage'] / 100) * float(insurance.price))

            print(f"Other Deduction Amount: {other_deduction_amount}")

            # If no insurance passed, default to account's insurance product
            insurance = insurance if insurance is not None else account.insurance_product

            # GOLD_LOAN flow: original logic
            if application.application_loan_type == LOAN_TYPE.GOLD_LOAN.value:

                print(f"Insurance: {insurance}")
                insurance_deduction = 0

                # Case 1: Insurance product matches the application's product
                if insurance.product == application.product:
                    insurance_deduction = insurance.price
                else:
                    print(account.insurance_amount_covered_from)
                    if account.insurance_amount_covered_from is None:
                        # Case 1: First-time insurance deduction
                        print("Case 1: First-time insurance deduction")
                        insurance_deduction = insurance.price
                    elif account.insurance_amount_covered_from and account.insurance_amount_covered_from.status == APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value:
                        # Case 2: Previous application rejected
                        print("Case 2: Previous insurance rejected")
                        insurance_deduction = 0
                        account.insurance_amount_covered_from = application
                        save_account = True
                    elif account.insurance_amount_covered_from.insurance_amount_deducted != insurance.price:
                        # Case 3: Insurance already deducted but with different amount
                        print(f"Case 3: Difference in insurance amount, {account.insurance_amount_covered_from.insurance_amount_deducted} vs {insurance.price}")
                        insurance_deduction = abs(insurance.price - account.insurance_amount_covered_from.insurance_amount_deducted)
                    elif application.application_type != "TAKEOVER" and account.insurance_amount_covered_from.insurance_amount_deducted == account.insurance_amount:
                        # Case 4: Insurance unchanged
                        print("Case 4: Insurance unchanged, no deduction needed")
                        insurance_deduction = 0

                # Apply insurance deduction and save application
                if source == 'nominee_add' and insurance_deduction > 0:
                    application.insurance_product = insurance
                    application.insurance_amount_deducted = insurance_deduction
                    print("insurance_deduction",insurance_deduction)
                    print("other_deduction_amount",other_deduction_amount)
                    print("before net_disbursed_amount",application.net_disbursed_amount)
                    application.save()
                    if application.product != insurance.product:
                        account.insurance_product = insurance
                        account.insurance_amount = insurance.price
                        print(f'Account insurance updated: {account.insurance_product}')
                        account.save()

                # Adjust net disbursed amount if necessary
                if application.application_type != "TAKEOVER" and source == 'nominee_add' and insurance_deduction > 0:
                    application.net_disbursed_amount = application.net_disbursed_amount - insurance_deduction - other_deduction_amount
                    print("After net_disbursed_amount",application.net_disbursed_amount)
                    application.save()

                # If marking paid, update the account's insurance record
                if source == 'marking_paid':
                    save_account = True
                    account.insurance_amount_covered_from = application

                if save_account:
                    account.save()

            # MSME_UNSECURED or WELLNESS loan flow
            elif application.application_loan_type in [LOAN_TYPE.MSME_UNSECURED.value, LOAN_TYPE.WELLNESS.value]:
                print(f"Handling loan type {application.application_loan_type}")
                insurance_deduction = insurance.price

                # Save insurance amount_v2 and update application
                application.insurance_product = insurance
                application.insurance_amount_deducted = insurance_deduction
                print(f'wellness/MSME-insurance_amount_deducted:insurance_deduction')
                application.net_disbursed_amount = application.net_disbursed_amount - insurance_deduction - other_deduction_amount
                application.save()

                # Optionally save account updates (if needed)
                if save_account:
                    account.save()

            else:
                print(f"Unhandled loan type: {application.application_loan_type}")

        except Exception as e:
            traceback.print_exc()


    def mark_insurance_paid(self, account, application, status):
        self.deduct_insurance_amount_from(application,source='marking_paid')
        """
         Below code handles if there are parallel applications and if they have selected different insurance products,
         then we update the below details again from insurance product previously saved in application model
        """
        if application.application_type=="TAKEOVER" and application.insurance_product and status==APPLICATION_STATUS.TAKEOVER_FIRST_DISBURSEMENT_DONE.value:
            account.insurance_product = application.insurance_product
            account.insurance_amount = application.insurance_product.price
            account.save()


        if status!=APPLICATION_STATUS.TAKEOVER_FIRST_DISBURSEMENT_DONE.value:
            Application.objects.exclude(Q(application_id=application.application_id)).exclude(Q(status__in=[APPLICATION_STATUS.TAKEOVER_FIRST_DISBURSEMENT_DONE.value,APPLICATION_STATUS.LOAN_DISBURSED.value, APPLICATION_STATUS.GOLD_COLLECTED.value, APPLICATION_STATUS.GOLD_DEPOSITED.value, APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value]))\
                .filter(account__account_id=account.account_id).update(net_disbursed_amount=F('net_disbursed_amount')+F('insurance_amount_deducted'),insurance_amount_deducted=0, insurance_product=None)
        else:
            Application.objects.exclude(Q(application_id=application.application_id)).exclude(
                Q(status__in=[APPLICATION_STATUS.TAKEOVER_FIRST_DISBURSEMENT_DONE.value,
                              APPLICATION_STATUS.LOAN_DISBURSED.value,
                              APPLICATION_STATUS.GOLD_COLLECTED.value,
                              APPLICATION_STATUS.GOLD_DEPOSITED.value,
                              APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value])) \
                .filter(account__account_id=account.account_id).update(
                insurance_amount_deducted=0, insurance_product=None)
            
    def calculate_age(self, dob):
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age