import datetime
import traceback

from minio import Minio, S3Error

from utils.envSetup import environment


class MinioUtility:

    def __init__(self):
        self.__minio_obj=self.__object_instance()
        env_type=environment.APP_ENV
        if env_type=='DEV':
            self.__bucket_name=environment.DEV_STORAGE_BUCKET_NAME
        else:
            self.__bucket_name = environment.PROD_STORAGE_BUCKET_NAME




    def __object_instance(self):
        raw_value = getattr(environment, "STORAGE_USE_SSL", None)
        if raw_value is not None:
            secure = str(raw_value).strip().lower() in {"1", "true", "yes", "on"}
        else:
            endpoint = (environment.STORAGE_ENDPOINT or "").strip().lower()
            secure = not (
                endpoint.startswith("localhost")
                or endpoint.startswith("127.0.0.1")
                or endpoint.startswith("host.docker.internal")
            )

        eos_client = Minio(endpoint=environment.STORAGE_ENDPOINT,
                           access_key=environment.STORAGE_ACCESS_KEY,
                           secret_key=environment.STORAGE_SECRET_KEY,
                           secure=secure)
        return eos_client


    def put_objects(self, file, path, name=None, file_size=None, content_type=None):
        try:
            file_name=file.name if name is None else name
            file_size=file_size if file_size is not None else file.size
            content_type=content_type if content_type is not None else file.content_type
            
            # Get extension from file name or content type
            ext = ""
            if "." in file_name:
                ext = "." + file_name.split(".")[-1]
            elif content_type:
                if "image" in content_type:
                    ext = "." + content_type.split("/")[-1]
                    if ext == ".jpeg": ext = ".jpg"
            
            # Remove environment prefix as bucket is already environment-specific
            object_name=path+'/'+file_name+f'_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}{ext}'
            result=self.__minio_obj.put_object(self.__bucket_name, object_name,
                                      file, file_size,
                                      content_type=content_type)

            print(result.__dict__)
            # Return the object name so it can be saved in the database
            return result.object_name
        except Exception as err:
            traceback.print_exc()
            raise err

    def upload_file_to_minio_by_path(self,file_path, object_name,file_name):
        try:
            # Upload the file to Minio
            object_name = object_name + '/' + file_name + f'_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.sql'
            result=self.__minio_obj.fput_object(self.__bucket_name, object_name, file_path)
            print(f"File uploaded to Minio: {self.__bucket_name}/{object_name}")
            print(result.__dict__)
            return result.__dict__
        except S3Error as e:
            print(f"Minio upload error: {e}")
        except Exception as e:
            print(f"Upload to Minio failed with error: {e}")
