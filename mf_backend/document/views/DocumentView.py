import base64

import requests
from PIL import Image
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from account.models import Account
from account.service.aadhar_mask import AadharMask
from osv2 import add_text_below_image
from utils.envSetup import environment
from ..utils.document_utils import DocumentUtils
from utils.responseHandler import HttpResponse
from utils.constants import ACCOUNT_STATUS, FORM_16, ADHAR_FRONT, ADHAR_BACK, PAN_CARD, APP_ENV, KYC_VENDORS , APPLICANT_TYPE
from document.models import Document
from ..serializers import DocumentDisplaySerializer, DocumentSerializer
import traceback


class DocumentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            doc=request.FILES['file']
            doc_size=doc.size / (1024 * 1024)
            if doc_size >= 10:
                return HttpResponse.Success({'msg': 'Please choose a file below 10MB'})
            account = Account.objects.get(account_id=request.GET.get('account_id',''))

            if not account:
                return HttpResponse.BadRequest('Account does not exist')
            doc_type=request.data.get('document_type')
            password = request.data.get('password', None)
            is_password=request.data.get('is_password')
            created=False

            # is_password = False
            # # Check if the document is password-protected for BANK_STATEMENT_1 and BANK_STATEMENT_2
            # if doc_type in ['BANK_STATEMENT_1', 'BANK_STATEMENT_2']:
            #     pdf_reader = PdfReader(doc)
            #     is_password = pdf_reader.is_encrypted

                
            if doc_type == ADHAR_FRONT or doc_type==ADHAR_BACK:
                kyc_vendor=environment.KYC_VENDOR
                if kyc_vendor==KYC_VENDORS.FRS.value:
                    masked_aadhar, name=AadharMask().mask_aadhar(data={'file': request.data.get('file')})
                    error = masked_aadhar.get('error', None)
                    status = masked_aadhar.get('data', {}).get('status', 'fail')
                    masked_aadhar = base64.b64decode(masked_aadhar.get('data', {}).get('file', None))
                    masked_aadhar=ContentFile(masked_aadhar, name=name)
                else:
                    back='aadhar' if doc_type==ADHAR_BACK else None
                    masked_aadhar, name=AadharMask().mask_aadhar_sprint_verify(data={'file': request.data.get('file')}, back=back)
                    error='Failed to mask aadhar' if masked_aadhar is None else None
                    status='pass' if masked_aadhar is not None else 'fail'
                    print(status, masked_aadhar)
                    if error is None:
                        masked_aadhar=requests.get(masked_aadhar)
                        masked_aadhar=ContentFile(masked_aadhar.content, name=name)

                print('mask error================>', error)

                env=environment.APP_ENV
                if doc_type!=ADHAR_BACK and error:
                    return HttpResponse.Success({'msg': 'Please take aadhar photo in portait mode and place aadhar properly'})

                if doc_type!=ADHAR_BACK and status!='pass':
                    return HttpResponse.Success({'msg':'Please upload valid photo of complete Aadhar.'})


                try:

                    obj = Document.objects.get(account=account, document_type=request.data.get('document_type'))
                    if error is None:
                        obj.file_name=name
                        obj.uploaded_by=request.user
                        obj.file=masked_aadhar
                        obj.is_password = is_password
                        obj.password = password
                        obj.save()

                    elif (error is not None and doc_type==ADHAR_BACK) or env!='PROD':
                        print('here')
                        print(doc)
                        obj.file_name = name
                        obj.uploaded_by = request.user
                        obj.file=doc
                        obj.is_password = is_password
                        obj.password = password
                        obj.save()


                    # elif env!='PROD':
                    #
                    #     name = doc.name
                    #     obj.file_name=name
                    #     obj.uploaded_by = request.user
                    #     obj.file=ContentFile(doc.read(), name=name)
                    #     obj.save()
                    resp = HttpResponse.Success({'asset': DocumentSerializer(obj).data})
                    created=False
                except ObjectDoesNotExist:
                    if error is None:
                        obj = Document(account=account,
                                       uploaded_by=request.user,
                                       document_type=request.data.get('document_type'),
                                       file_name=name,file=masked_aadhar,
                                       is_password = is_password,
                                       password=password)

                        obj.save()

                    elif (error is not None and doc_type==ADHAR_BACK) or env!='PROD':
                        print(doc)
                        obj = Document(account=account,
                                       uploaded_by=request.user,
                                       document_type=request.data.get('document_type'),
                                       file_name=name,
                                       is_password = is_password,
                                       )
                        obj.file=doc
                        obj.save()

                    # elif :
                    #     file = request.data.get('file')
                    #     name = file.name
                    #     obj = Document(account=account,
                    #                    uploaded_by=request.user,
                    #                    document_type=request.data.get('document_type'),
                    #                    file_name=name, file=ContentFile(file.read(), name=name))

                    #     obj.save()
                    resp = HttpResponse.Success({'asset': DocumentSerializer(obj).data})
                    created = True
                except:
                    traceback.print_exc()

            else:
                document_serialized = DocumentUtils(request.user).upload_document_new(file=request.data.get('file'),document_type=request.data.get('document_type'),account=str(account))

                if document_serialized.is_valid():


                    # document_serialized.save()
                    obj, created = Document.objects.update_or_create(
                            account=account,
                            document_type=request.data.get('document_type'),
                            defaults=document_serialized.validated_data,
                        )
                    obj.is_password = is_password
                    obj.password = password
                    obj.save()
                    resp=HttpResponse.Success({'asset':DocumentSerializer(obj).data})
                else:
                    resp=HttpResponse.BadRequest({'errors':document_serialized.errors})
            if doc_type in [ADHAR_FRONT,ADHAR_BACK,PAN_CARD,FORM_16]:
                self.__mark_kyc_added(account, created=created,data=request.data)

            if doc_type in ['ADHAR_FRONT', 'ADHAR_BACK', 'PAN_CARD']:
                username = request.user.username
                employee_id = request.user.employee_id
                # image = Image.open(doc)
                image = Image.open(masked_aadhar if doc_type in [ADHAR_FRONT, ADHAR_BACK] else doc)

                modified_image = add_text_below_image(image, username, employee_id)
                modified_image_name = f"{obj.file_name}_modified.jpg"
                obj.file_name = modified_image_name
                obj.file.save(modified_image_name, ContentFile(modified_image.read()), save=True)
            # print(1)
            # resp = HttpResponse.Success({'asset': ser.data})    
            
            return resp
        except Exception as e:
            
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def __aadhar_pan_check(self, account, docs):
        if account.pan_no:
            return account.aadhar_verified and account.pan_verified
        else:
            return FORM_16 in docs and account.aadhar_verified


    def __mark_kyc_added(self, account, created, data):
        docs = list(Document.objects.values_list('document_type', flat=True).filter(account=account,
                                                                                    document_type__in=[ADHAR_FRONT,
                                                                                                       ADHAR_BACK,
                                                                                                       PAN_CARD,
                                                                                                       FORM_16]))

        if len(docs) >= 3:
            # all_docs_uploaded = self.__aadhar_pan_check(account, docs)
            if (account.status!=ACCOUNT_STATUS.ACCOUNT_CONFIRMED.value) and (account.status!=ACCOUNT_STATUS.NOMINEE_ADDED.value) and (created and data.get('document_type') in [ADHAR_FRONT, ADHAR_BACK, PAN_CARD,
                                                                 'FORM_16'] and self.__aadhar_pan_check(account, docs)):
                if account.applicant_type==APPLICANT_TYPE.CO_APPLICANT.value:
                    applicant=Account.objects.get(user=account.applicant)
                    applicant.status=ACCOUNT_STATUS.CO_APPLICANT_KYC_ADDED.value
                    applicant.save()
                    account.status = ACCOUNT_STATUS.CO_APPLICANT_KYC_ADDED.value
                else:
                    account.status = ACCOUNT_STATUS.KYC_ADDED.value
                account.save()

    def get(self, request, *args, **kwargs):
        try:
            account = Account.objects.get(account_id=request.GET.get('account_id',''))
           
            docs = Document.objects.filter(account=account)
            ser=DocumentDisplaySerializer(docs,many=True)
            
            resp=HttpResponse.Success({
                'account_documents':ser.data,
                'aadhar_no': account.aadhar_no,
                'aadhar_verified': account.aadhar_verified,
                'pan_no': account.pan_no,
                'pan_verified': account.pan_verified,
            })
            return resp
        except Exception as e:
            
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def delete(self, request, *args, **kwargs):
        try:
            document_type=request.GET.get('document_type','')
            doc = Document.objects.get(document_type=document_type, account__account_id=request.GET.get('account_id',''))
            doc.delete()

            if document_type == PAN_CARD:
                doc.account.pan_verified = False
                doc.account.pan_no = None
                doc.account.save()
            
            resp=HttpResponse.Success({"msg": "Document deleted successfully."})
            return resp
        except Document.DoesNotExist as de:
            return HttpResponse.BadRequest(str(de))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        


        

        