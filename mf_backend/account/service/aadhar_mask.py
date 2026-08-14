from account.service.sprint_verify_docs import SprintVerifyDocs
from utility.frs.frs_utilities import Frs


class AadharMask:


    def mask_aadhar(self, data):
        frs=Frs()
        payload = {'mask_qr':True,'rotate':True}
        uploaded_file = data.get('file')
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.content_type)}
        result = frs.mask_aadhar(data=payload, files=files)
        return result, uploaded_file.name

    def mask_aadhar_sprint_verify(self, data, back):
        uploaded_file = data.get('file')
        result = SprintVerifyDocs().mask_aadhar(file=uploaded_file, back=back)
        print(result)
        result = result.get('data').get('masked_image', None)

        return result, uploaded_file.name