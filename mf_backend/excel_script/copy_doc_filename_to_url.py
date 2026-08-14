# iterate on 3 models: asset doc, loan doc, document
from application.models import AssetDocuments , LoanDocument
from document.models import Document
import os



def DocScript():
    try:
        docs = Document.objects.all()
        

        for doc in docs:
            file_name = (doc.file_name)
            print(file_name)
            if not doc.url:
                file_name = file_name.strip()
                doc.url = os.path.join("https://mum-objectstore.e2enetworks.net/radian/media/" + doc.file_name)
                doc.save()
            print(doc.url)
                

    except Exception as e:
        print(f"An error occurred: {str(e)}")

DocScript()

def assetDocScript():
    try:
        docs = AssetDocuments.objects.all()
        

        for doc in docs:
            file_name = (doc.file_name)
            print(file_name)
            if not doc.url:
                file_name = file_name.strip()
                doc.url = os.path.join("https://mum-objectstore.e2enetworks.net/radian/media/" + doc.file_name)
                doc.save()
            print(doc.url)
                

    except Exception as e:
        print(f"An error occurred: {str(e)}")

assetDocScript()

def loanDocScript():
    try:
        docs = LoanDocument.objects.all()
        

        for doc in docs:
            file_name = (doc.file_name)
            print(file_name)
            if not doc.url:
                file_name = file_name.strip()
                doc.url = os.path.join("https://mum-objectstore.e2enetworks.net/radian/media/" + doc.file_name)
                doc.save()
            print(doc.url)
                

    except Exception as e:
        print(f"An error occurred: {str(e)}")

loanDocScript()






"""
python3 manage.py shell
exec(open('excel_script/copy_doc_filename_to_url.py').read())
"""

