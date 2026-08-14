from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from account.models import Account
from application.models import Application
from lender.models import Lender
from lender.serializers import LenderSerializer
from loan.models import TakeOverResidenceAddress
from loan.serializer import GPRSDocSerializer
from loan.serializers.loan_take_over_serializer import TakeOverResidenceDetailsSerializer
from utility.common_utils import custom_response_obj
from utility.crud_helper import CrudHelper
from utils.constants import APPLICATION_STATUS


class TakeoverResidenceService:

    __take_over_crud_service=CrudHelper(TakeOverResidenceDetailsSerializer)
    __residence_inspection_doc=CrudHelper(GPRSDocSerializer)
    def add_takeover_residence(self, data, application_id):
        account=self.__validate_account(account=data.get('account'))
        if account:
            try:
                bt_inspection = TakeOverResidenceAddress.objects.get(account__account_id=data.get('account'))
                data=self.__take_over_crud_service.update_obj(data=data, update_key_value=bt_inspection.take_over_residence_details_id)
            except ObjectDoesNotExist:
                data= self.__take_over_crud_service.add_obj(data=data)
            application=self.__update_application(application_id)
            response_data=data.get('data')
            response_data['lender']=LenderSerializer(Lender.objects.get(lender_id=application.lender.lender_id)).data
            data['data']=response_data
            return data
        return custom_response_obj(message={'msg':'Invalid account'}, code=200 , error_msg={'msg':'Invalid account'},
                                   error_code=200)

    def __update_application(self, application_id):
        application = Application.objects.get(application_id=application_id)
        if application.status == APPLICATION_STATUS.TAKE_OVER_LOAN_INITIATED.value:
            application.status = APPLICATION_STATUS.BT_RESIDENCE_ADDED.value
        elif application.status==APPLICATION_STATUS.LOAN_AMOUNT_ADDED.value:
            application.status=APPLICATION_STATUS.RESIDENCE_ADDED.value
        application.save()
        return application

    def __get_application_lender_data(self, application):
        application = Application.objects.get(application_id=application)
        return LenderSerializer(Lender.objects.get(lender_id=application.lender.lender_id)).data

    def __validate_account(self, account):
        try:
            account=Account.objects.get(account_id=account)
            return account
        except ObjectDoesNotExist:
            return None

    def get_account_details(self, account_id, application):
        data=self.__take_over_crud_service.get_all_data(query=Q(account__account_id=account_id))
        if len(data['data']) > 0:
            data['data']=data['data'][0]
            data['data']['lender']=self.__get_application_lender_data(application=application)
        else:
            data['data']={}
        return data

    def update_details(self, data,takeover_residence_id, application_id):
        self.__update_application(application_id)
        return self.__take_over_crud_service.update_obj(data=data, update_key_value=takeover_residence_id)

    def delete_details(self, takeover_residence_id):
        return self.__take_over_crud_service.delete_obj(takeover_residence_id)


    def add_docs(self, data):
        try:
            bt_inspection=TakeOverResidenceAddress.objects.get(account__account_id=data.get('account_id'))
            data['take_over_residence']=bt_inspection.take_over_residence_details_id
        except ObjectDoesNotExist:
            bt_inspection=self.__take_over_crud_service.add_obj(data={'account':data.get('account_id')})
            data['take_over_residence']=bt_inspection.get('data',{}).get('take_over_residence_details_id')

        result=self.__residence_inspection_doc.add_obj(data=data)
        return custom_response_obj(message={'inspection_doc':result.get('data')}, code=result.get('status_code'))

    def get_data(self, take_over_residence_id):
        return self.__residence_inspection_doc.get_all_data(Q(take_over_residence__take_over_residence_details_id=take_over_residence_id))

    def update_docs(self, take_over_id, data):
        return self.__residence_inspection_doc.update_obj(data=data, update_key_value=take_over_id)
    def delete_docs(self, takeover_id):
        return self.__residence_inspection_doc.delete_obj(takeover_id)
