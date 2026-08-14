import os
import traceback


from application.models import AssetDocuments, LoanDocument
from document.models import Document
from mimetypes import MimeTypes
from utils.envSetup import environment
from minio import Minio, S3Error

mime = MimeTypes()
class MinioUtility:

    def __init__(self):

        self.count = 0
        self.not_found_file = []
        self.__minio_obj=self.__object_instance()
        self.__bucket_name='radian'



    def __object_instance(self):
        eos_client = Minio(endpoint='mum-objectstore.e2enetworks.net',
                           access_key=environment.STORAGE_ACCESS_KEY,
                           secret_key=environment.STORAGE_SECRET_KEY,
                           secure=False)
        return eos_client


    def put_objects(self, file, path):
        try:
            print(file.path)
            if os.path.isfile(file.path):
                object_name = path + file.name
                mime_type = mime.guess_type(file.path)
                print(mime_type)
                mime_type = mime_type[0]
                
                result=self.__minio_obj.fput_object(self.__bucket_name, object_name, file.path, content_type=mime_type)

                print(result.__dict__)
                self.count += 1
                return result.__dict__
            else:
                self.not_found_file.append(file.path)

        except Exception as err:
            print(err)
            traceback.print_exc()


minio = MinioUtility()


def upload():
    asset_docs = AssetDocuments.objects.all()
    for doc in asset_docs:
        minio.put_objects(doc.file, 'media/asset_doc/')

    loan_docs = LoanDocument.objects.all()
    for doc in loan_docs:
        minio.put_objects(doc.file, 'media/loan_doc/')

    docs = Document.objects.all()
    for doc in docs:
        minio.put_objects(doc.file, 'media/doc/')

    print("Uploaded files: "+str(minio.count))

    print("Not found files: "+str(len(minio.not_found_file)))
    print(minio.not_found_file)

upload()




# # from minio.error import ResponseError
# from utils.envSetup import environment
# from django.conf import settings
# from mimetypes import MimeTypes
# from minio import Minio, S3Error

# import os
# import traceback


# def handle():
    
#     try:
#         mime = MimeTypes()
#         media_root = getattr(settings, 'MEDIA_ROOT', None)
#         bucket_name=environment.STORAGE_BUCKET_NAME
#         eos_client = Minio(endpoint='mum-objectstore.e2enetworks.net',
#                             access_key=environment.STORAGE_ACCESS_KEY,
#                             secret_key=environment.STORAGE_SECRET_KEY,
#                             secure=False)
        

#         for filename in os.listdir(media_root):
#             f = os.path.join(media_root, filename)
#             # checking if it is a file
#             if os.path.isfile(f):
#                 print(filename)
#                 mime_type = mime.guess_type(f)
#                 with open(f, 'rb') as file_data:

#                     file_stat = os.stat(f)
#                     eos_client.put_object(bucket_name, filename,
#                                         file_data, file_stat.st_size,
#                                         content_type=mime_type)

#     except S3Error as e:
#         print(f"Minio upload error: {e}")
#     except Exception as err:
#         print(err)
#         traceback.print_exc()


# handle()

"""
python3 manage.py shell
exec(open('excel_script/bulk_upload_on_bucket.py').read())
"""


# from application.models import AssetDocuments, LoanDocument
# d = AssetDocuments.objects.all().first()
# print(d.file.path)


# DB Migration:
# 1. Take backup of media files and database.
# 2. sudo docker builder prune -a
# 3. Whithout taking latest code just execute bulk_upload_on_bucket.py file on server
# 4. take pull to fetch db migration code and execute altering_db_record.py file


# uploaded 4070 files from UAT to bucket
