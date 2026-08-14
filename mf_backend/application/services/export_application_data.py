from application.models import Application , ApplicationGoodsMapping 
from account.models import BankAccount , NomineeDetails
from django.db.models import Q
from loan.models import LoanEMISchedule , LoanEMIRecord
from itertools import zip_longest
from utils.constants import ADDRESS_TYPE

"""
Might replace with subquery for better performance
# subquery = Subquery(
          #     ApplicationGoodsMapping.objects.filter(
          #         application=OuterRef('pk'),
          #     ).exclude(pk=OuterRef('pk')).values_list('goods__goods_name', flat=True),
          #     output_field=models.JSONField()
          # )
          # application=Application.objects.annotate(agm_goods_names=Subquery(
          #               ApplicationGoodsMapping.objects.filter(
          #                   application=OuterRef('pk'),
          #               ).values('goods__goods_name'),
          #               output_field=models.JSONField()
          #           ))
          # subquery = Subquery(
          #     ApplicationGoodsMapping.objects.filter(
          #         application=OuterRef('pk'),
          #     ).values('goods__goods_name'),
          #     output_field=models.TextField()
          # )
"""
class ExportApplicationService():


     def get_goods_for_application(self,application):
          goods = ApplicationGoodsMapping.objects.filter(application=application)
          goods_list = [goods_item.goods.goods_name for goods_item in goods]
          return ", ".join(goods_list)



     def get_application_data(self,query_options={}):
          query_options_available = ['application_id__in','created_at__gte', 'created_at__lte', 'status', 'disbursed_date__gte',
                                          'disbursed_date__gte', 'purpose of loan', 'loan_amount_range__gte',
                                          'loan_amount_range__lte', 'product_id', 'product_name', 'product_lender_name',
                                          'total_weight__gte', 'total_weight__lte', 'net_weight__gte', 'net_weight__lte',
                                          'application_type', 'originated_by', 'amortization_type', 'tenure__gte',
                                          'tenure'
                                          ]


          filter_query = {}
          if len(query_options)>0:
               for i in query_options_available:
                    opt = query_options.get(i)
                    if opt is not None:
                         if i =='application_id__in':
                              opt=opt.split(",")
                         filter_query[i] = opt

          applications = Application.objects.filter(**filter_query).prefetch_related(
               'agmMap_application',
               'account__bankaccount_account',
               'account__nomieedetails_account',
               'loan_take_over_app',
               'loan_application',
               'asset_application',
               'account__insurance_product',
               'account__user_addresse'
          )
          applicationData = []

          for application in applications:
               bank_details = application.account.bankaccount_account.all().first()
               nominee_details = application.account.nomieedetails_account.all().first()
               loan_takeover_details = application.loan_take_over_app.all().first()
               loan_details = application.loan_application.all().first()
               asset_details = application.asset_application.all().first()
               insurance_details = application.account.insurance_product
               loan_emi_schedule = LoanEMISchedule.objects.filter(application=application).first()
               loan_emi_records = LoanEMIRecord.objects.filter(loan_emi_header=loan_emi_schedule)
               goods_names = ", ".join(application.agmMap_application.values_list('goods__goods_name', flat=True))
               permanent_address = application.account.user_addresse.filter(
                    address_type=ADDRESS_TYPE.PERMANENT_ADDRESS.value
                    ).first()

               # Default value if no permanent address exists
               formatted_address = "None"

               if permanent_address:
                    # Format the address details into a single string
                    formatted_address = ", ".join(
                         filter(
                              None,  # Filter out None or empty values
                              [
                                   permanent_address.building_name,
                                   permanent_address.street_name,
                                   permanent_address.city,
                                   permanent_address.state,
                                   permanent_address.pincode,
                                   permanent_address.country,
                              ],
                         )
                    )

               single_application_data = [
                    application.account.user.get_full_name(),
                    application.account.customer_id,
                    loan_details.loan_number if loan_details else "",
                    application.account.email,
                    application.account.gender,
                    application.account.year_of_birth.strftime("%d/%m/%Y"),
                    application.account.user.phone,
                    formatted_address,
                    application.account.occupation,
                    application.account.net_annual_income,
                    application.account.aadhar_no,
                    application.account.pan_no,
                    application.account.mother_name,
                    application.account.father_name,
                    application.account.spouse_name,
                    application.account.education,
                    application.account.religion,
                    application.account.nationality,
                    application.account.caste,
                    bank_details.bank_name if bank_details else "",
                    bank_details.account_number if bank_details else "",
                    bank_details.ifsc if bank_details else "",
                    bank_details.account_holder_name if bank_details else "",
                    application.branch.branch_code if application.branch else "",
                    application.branch.branch_name if application.branch else "",
                    application.branch.state if application.branch else "",
                    application.status,
                    application.application_number,
                    application.purpose_of_loan,
                    application.loan_amount,
                    application.contra_loan_amount,
                    application.product.product_name if application.product else "",
                    application.product.lender.lender_name if application.product else "",
                    goods_names,
                    application.total_goods_price,
                    application.total_gross_weight,
                    application.total_wastage,
                    application.net_weight,
                    # asset_details.karat_value if asset_details else "",
                    application.application_type,
                    insurance_details.product_name if insurance_details else "",
                    insurance_details.coverage if insurance_details else "",
                    insurance_details.price if insurance_details else "",
                    loan_takeover_details.lender_name if loan_takeover_details else "",
                    loan_takeover_details.loan_amount if loan_takeover_details else "",
                    loan_takeover_details.requested_amount_from_radian if loan_takeover_details else "",
                    loan_takeover_details.total_release_amount if loan_takeover_details else "",
                    loan_takeover_details.loan_start_date if loan_takeover_details else "",
                    loan_takeover_details.maturity_date if loan_takeover_details else "",
                    loan_takeover_details.loan_reference_number if loan_takeover_details else "",
                    float(loan_takeover_details.gold_weight_pledged) if loan_takeover_details else "",
                    loan_emi_records.order_by('created_at').first().due_date if loan_emi_records else "", #emi_start_date 
                    loan_emi_records.order_by('-created_at').first().due_date  if loan_emi_records else "", #loan_maturity_date
                    application.Originatedby.get_full_name(),
                    application.appraisedBy.get_full_name() if application.appraisedBy else "",
                    nominee_details.first_name+" "+nominee_details.last_name if nominee_details else "",
                    nominee_details.age if nominee_details else "",
                    nominee_details.relation if nominee_details else "",
                    nominee_details.contact_no if nominee_details else "",
                    application.tenure,
                    application.intrest_rate,
                    application.processing_fee,
                    float(application.processing_fee_percent),
                    application.amortization_type,
                    application.penalty,
                    application.gst,
                    application.stamp_duty,
                    application.ltv,
                    application.gold_rate_per_gram,
                    application.disbursal_amount,
                    application.disbursed_date.strftime("%d/%m/%Y") if application.disbursed_date else "",
                    application.created_at.strftime("%d/%m/%Y, %H:%M")
               ]

               applicationData.append(single_application_data)

          return applicationData