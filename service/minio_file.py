from datetime import timedelta
from http.client import HTTPException
from config.minio_client import MinioClient
from fastapi import UploadFile
from minio.error import S3Error
from schema.pydantic_schema import MinIOUploadResponse

class MinIOFileService:
    def upload(bucket_name:str, file:UploadFile):
        try:
            MinioClient.client.put_object(
                bucket_name,
                file.filename,
                file.file,
                length=-1,
                part_size=MinioClient.part_size
            )
            url = MinioClient.client.presigned_get_object(bucket_name, file.filename, expires=timedelta(hours=1))
            return MinIOUploadResponse(filename=file.filename, url=url).model_dump()
        except S3Error as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def download(bucket_name:str, filename:str):
        try:
            url = MinioClient.client.presigned_get_object(bucket_name, filename, expires=timedelta(hours=1))
            return MinIOUploadResponse(filename=filename, url=url).model_dump()
        except S3Error as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def create_bucket_startup():
        try:
            if not MinioClient.client.bucket_exists(MinioClient.bucket_name):
                print("Creating new bucket")
                MinioClient.client.make_bucket(MinioClient.bucket_name)
            else:
                print("Bucket is found, and ready to use")
        except S3Error as e:
            print(e)
