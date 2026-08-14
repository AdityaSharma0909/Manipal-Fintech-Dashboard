

# from minio.error import ResponseError
from utils.envSetup import environment
from django.conf import settings
from mimetypes import MimeTypes
from minio import Minio, S3Error

import os
import traceback


def handle():
    
    try:
        mime = MimeTypes()
        bucket_name='uat-backup-files'
        eos_client = Minio(endpoint='mum-objectstore.e2enetworks.net',
                            access_key='4NUE88K5WYDMGK1Z9I21',
                            secret_key='4SQXWJDD62GJZA6YA24I9QHEDRLWYXJKUXWHZOHB',
                            secure=False)
        

        rootPath = 'unused_files/unused_files'
        for filename in os.listdir(rootPath):
            f = os.path.join(rootPath, filename)
            # checking if it is a file
            print(f)
            if os.path.isfile(f):

                with open(f, "rb") as file_data:
                    object_name = 'unused_files/'+filename
                    mime_type = mime.guess_type(f)

                    print(bucket_name)
                    print(type(bucket_name))
                    print("\n")
                    print(object_name)
                    print("\n")
                    print(f)
                    print(type(f))
                    print("\n")
                    print(mime_type)
                    print(type(mime_type))
                    print("\n")

                    file_size = os.stat(f).st_size
                    result=eos_client.put_object(bucket_name, object_name, file_data, file_size, content_type=mime_type)

                    print(result)

    except S3Error as e:
        print(f"Minio upload error: {e}")
    except Exception as err:
        print(err)
        traceback.print_exc()


handle()

"""
python3 manage.py shell
exec(open('excel_script/raw_bulk_upload_on_bucket.py').read())
"""
