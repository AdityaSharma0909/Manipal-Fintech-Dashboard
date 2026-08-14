import datetime
import traceback

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from account.serializers import AccountModelSerializer, CustomerDisplayAccountSerializer, VerificationUpdateSerializer, \
    AccountCreationSerializer
from document.utils.document_utils import DocumentUtils
from loan.models import GprsPhotos
from loan.serializer import GPRSDocSerializer
from users.models import User
from application.models import Application
from account.models import Account
from users.service.otpService import OtpService
from utility.common_utils import serializer_instance, custom_response_obj
from utility.crud_helper import CrudHelper
from utils.constants import CODE_OF_STATES, OTP_TYPE, ACCOUNT_STATUS ,ROLES
import utils.helper as helper
from rest_framework import serializers
from rest_framework.response import Response
import random
import math




## displaying the random string
class AccountService:

    account_instance=CrudHelper(CustomerDisplayAccountSerializer)
    account_creation=CrudHelper(AccountCreationSerializer)
    def generate_cif_number(self):

        state_code=CODE_OF_STATES.MAHARASTRA.value
        current_date = str(datetime.date.today())
        year=current_date[2:4]
        number=helper.generate_numbers(6)

        return "RF"+state_code+year+str(number)

    def generate_third_party_cif_number(self):
        year=str(datetime.date.today().year)[2:4]
        number = helper.generate_numbers(6)
        return "RFTP"+year+str(number)



    def check_if_account_exist(self, data):
        try:
            user_exist=get_user_model().objects.get(phone=data['phone'])
            return user_exist

        except Exception:
            return None

    def delete_account(self, account_id):
        return self.account_instance.delete_obj(account_id)



    def account_kyc_verification(self, account_id, data):
        try:
            account=Account.objects.get(account_id=account_id)
            if 'aadhar_no' in data.keys() and len(str(data.get('aadhar_no')))==12:
                data['aadhar_no']=self.__mask_aadhar(data.get('aadhar_no'))
            return serializer_instance(VerificationUpdateSerializer, data=data, instance=account, partial=True)
        except Exception:
            traceback.print_exc()


    def __mask_aadhar(self, aadhar):
        print("aadhar")
        aadhar_mask=''.join(['x' for i in range(8)])+str(aadhar)[8:12]
        print("masked", aadhar_mask)
        return aadhar_mask


    def verify_mobile_number_otp(self, account_id):
        try:

            resp={'otp':OtpService().generate_otp(user=None,otp_type=OTP_TYPE.ACCOUNT_PHONE_VERIFICATION_OTP.value,

                                                  user_mobile_number=account_id),
                'phone':str(account_id)}

            return custom_response_obj(message=resp,code=200)
        except Exception:
            traceback.print_exc()


    def update_branch_for_all_accounts(self):
        account=Account.objects.filter(branch__isnull=True)
        updated_list=[]
        not_found=[]
        for i in account:
            branch=i.created_by.lm_branch_map.first()
            if branch:
                i.branch=branch
                updated_list.append(i.customer_id)
            else:
                not_found.append(i.customer_id)
            i.save()
        return {'updated_accounts':updated_list, 'failed_account':not_found, 'total_updated':len(updated_list),
                'failed':len(not_found)}


    def create_account(self, user, data, created_by):
        cif=self.generate_third_party_cif_number()
        profile_pic=data.get('profile_photo', None)
        if profile_pic:
            profile_pic = DocumentUtils(user).upload_document(file=profile_pic,document_type="CUSTOMER_PROFILE_PIC")
        data["customer_id"] = str(cif)
        data['user'] = user.user_id
        data['created_by'] = created_by.user_id
        data['profile_photo'] = profile_pic.document_id
        response=self.account_creation.add_obj(data)
        return response


    def verify_kyc_for_third_party(self, account_id):
        try:
            print(account_id)
            account=Account.objects.get(account_id=account_id)
            verify_kyc=account.aadhar_verified and account.pan_verified
            banks=account.bankaccount_account.all().first()
            if banks and verify_kyc:
                verify_kyc=verify_kyc and banks.verified
            else:
                verify_kyc=False
            return custom_response_obj(message={'kyc_verified':verify_kyc,
                                                       'aadhar_verified':account.aadhar_verified,
                                                       'pan_verified':account.pan_verified,
                                                       'bank_account_verified':banks.verified}, code=200)
        except ObjectDoesNotExist:
            return custom_response_obj(message={'msg':f'account with id {account_id} not found'}, code=404,
                                       error_msg={'msg':f'account with id {account_id} not found'}, error_code=404)



    # def upload_gprs_photo(self, data):
    #     data=serializer_instance(GPRSDocSerializer,data=data)
    #     print(data)
    #     return data

    def upload_gprs_photo(self, data, account_id, application_id, user):
        ser = GPRSDocSerializer(data=data)
        data["account"] = account_id
        data['application'] = application_id
        if ser.is_valid():
            ser.save()
            # account_id = data['account']
            try:
                account = Account.objects.get(account_id=account_id)
            except Account.DoesNotExist:
                raise serializers.ValidationError("Account with the provided ID does not exist.")
            # if user.role == ROLES.RELATIONSHIP_MANAGER.value:
            #     relationship_manager_photo_types = [
            #         "IMAGE_OF_HOUSE_WITH_PERSON_STANDING_AT_THE_GATE",
            #         "IMAGE_OF_SHOP_WITH_PERSON_STANDING_AT_THE_GATE",
            #         "IMAGE_OF_INSIDE_THE_SHOP"
            #     ]
            #     existing_photo_types = set(account.account_gprs_photos.filter(
            #         photo_type__in=relationship_manager_photo_types
            #     ).values_list('photo_type', flat=True))
                    
            #     if account.status == ACCOUNT_STATUS.REFERENCE_PD_ADDED.value and set(relationship_manager_photo_types).issubset(existing_photo_types):
            #             account.status = ACCOUNT_STATUS.RESIDENCE_PROOF_ADDED.value
            #             account.save()

            if user.role == ROLES.RELATIONSHIP_MANAGER.value:
                existing_photo_types = set(account.account_gprs_photos.values_list('photo_type', flat=True))
            
                if account.status == ACCOUNT_STATUS.REFERENCE_PD_ADDED.value and len(existing_photo_types) >= 3:
                    account.status = ACCOUNT_STATUS.RESIDENCE_PROOF_ADDED.value
                    account.save()

            elif user.role == ROLES.CREDIT_OFFICER.value:
                try:
                    if application_id is None:
                        # return Response(data={'msg': 'application_id is required'}, status=200)
                        return custom_response_obj(message='application_id is required', code=500)
                    application = Application.objects.get(application_id=application_id)
                    
                except Application.DoesNotExist:
                    raise serializers.ValidationError("Application with the provided ID does not exist.")
                # credit_officer_photo_types = [
                #     "CO_IMAGE_OF_HOUSE_WITH_PERSON_STANDING_AT_THE_GATE",
                #     "CO_IMAGE_OF_SHOP_WITH_PERSON_STANDING_AT_THE_GATE",
                #     "CO_IMAGE_OF_INSIDE_THE_SHOP",
                #     "CO_OTHERS",
                # ]
                # existing_photo_types = set(application.application_gprs_photos.filter(
                #     photo_type__in=credit_officer_photo_types
                # ).values_list('photo_type', flat=True))

        return custom_response_obj(message={'inspection_doc': ser.data}, code=200)

    def change_status(self, account_id):
        account_id=Account.objects.get(account_id=account_id)
        if account_id.status==ACCOUNT_STATUS.REFERENCE_PD_ADDED.value:
            account_id.status=ACCOUNT_STATUS.RESIDENCE_PROOF_ADDED.value
            account_id.save()
            return custom_response_obj(message={'msg':'Account status updates successfully'}, code=200)
        return custom_response_obj(message={'msg': 'Please add Reference PD first'}, code=200)

    def delete_gprs_photo(self, gprs_photo_id):
        data=GprsPhotos.objects.get( gprs_photos_id=gprs_photo_id).delete()
        return custom_response_obj(message={'msg': 'Photo deleted successfully'}, code=200)

    # def get_gprs_photos(self, request,account_id):
    #     user = request.user
    #     if user.role == ROLES.RELATIONSHIP_MANAGER.value :
    #         pass
    #     elif user.role == ROLES.CREDIT_OFFICER.value:
    #         pass
        
    #     # data=list(GprsPhotos.objects.values().filter(account=account_id))
    #     # return custom_response_obj(message={'inspection_doc': data}, code=200)
    #     gprs = GprsPhotos.objects.filter(account=account_id)
    #     serializer = GPRSDocSerializer(gprs , many=True)
    #     return custom_response_obj(message={'inspection_doc': serializer.data}, code=200)
    
    def get_gprs_photos(self, account_id, application_id, user):
        gprs = GprsPhotos.objects.filter(account=account_id)
        
        # # Define the photo types for each role
        # relationship_manager_photo_types = [
        #     "IMAGE_OF_HOUSE_WITH_PERSON_STANDING_AT_THE_GATE",
        #     "IMAGE_OF_SHOP_WITH_PERSON_STANDING_AT_THE_GATE",
        #     "IMAGE_OF_INSIDE_THE_SHOP",
        #     "OTHERS",
        # ]
        # credit_officer_photo_types = [
        #     "CO_IMAGE_OF_HOUSE_WITH_PERSON_STANDING_AT_THE_GATE",
        #     "CO_IMAGE_OF_SHOP_WITH_PERSON_STANDING_AT_THE_GATE",
        #     "CO_IMAGE_OF_INSIDE_THE_SHOP",
        #     "CO_OTHERS",
        # ]

        account = Account.objects.get(account_id=account_id)
        # Apply role-specific filtering
        if user.role == ROLES.RELATIONSHIP_MANAGER.value:
            # gprs = gprs.filter(photo_type__in=relationship_manager_photo_types)
            gprs = account.account_gprs_photos.filter(application_id__isnull=True)
            
        elif user.role == ROLES.CREDIT_OFFICER.value:
            if application_id is None:
                # return Response(data={'msg': 'application_id is required'}, status=200)
                return custom_response_obj(message='application_id is required', code=500)
            application = Application.objects.get(application_id=application_id)
            # gprs = gprs.filter(photo_type__in=credit_officer_photo_types)
            gprs =  application.application_gprs_photos.all()

        # Serialize and return the data
        serializer = GPRSDocSerializer(gprs, many=True)
        return custom_response_obj(message={'inspection_doc': serializer.data}, code=200)

