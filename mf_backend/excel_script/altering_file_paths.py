# iterate on 3 models: asset doc, loan doc, document
from application.models import AssetDocuments , LoanDocument
from document.models import Document
import os

BUCKET_NAME = 'radian'
STORAGE_ENDPOINT = "https://mum-objectstore.e2enetworks.net"

class Script():
    dc = 0
    ac = 0 
    lc = 0

    def DocScript(self):
        try:
            docs = Document.objects.all()
            
            for doc in docs:
                if doc.file and 'media/doc' not in str(doc.file):
                    doc.file = "media/doc/" + str(doc.file)
                    doc.save()
                    self.dc += + 1
                print(doc.file)
                    

        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def assetDocScript(self):
        try:
            docs = AssetDocuments.objects.all()
            
            for doc in docs:
                if doc.file and 'media/asset_doc' not in str(doc.file):
                    doc.file = "media/asset_doc/" + str(doc.file)
                    doc.save()
                    self.ac += + 1
                print(doc.file)
                    

        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def loanDocScript(self):
        try:
            docs = LoanDocument.objects.all()
            
            for doc in docs:
                if doc.file and 'media/loan_doc' not in str(doc.file):
                    doc.file = "media/loan_doc/" + str(doc.file)
                    doc.save()
                    self.lc += + 1
                print(doc.file)
                    

        except Exception as e:
            print(f"An error occurred: {str(e)}")


script = Script()
script.DocScript()
script.assetDocScript()
script.loanDocScript()

print(script.dc)
print(script.ac)
print(script.lc)



"""
python3 manage.py shell
exec(open('excel_script/altering_file_paths.py').read())
"""

