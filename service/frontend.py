from datetime import datetime, timedelta
from fastapi import UploadFile, HTTPException
import pytz
from config.minio_client import MinioClient
from uuid import uuid4
from minio import S3Error
from sqlalchemy.orm import Session

from model.database_model import Upload


class FrontendService:
    def upload(db:Session, bucket_name:str, file:UploadFile, uploader:str, email:str):
        now_jakarta = datetime.now(tz=pytz.timezone("Asia/Jakarta"))
        minio_object_filename = f"{now_jakarta}_{uuid4()}_{file.filename}"
        try:
            MinioClient.client.put_object(
                bucket_name,
                minio_object_filename,
                file.file,
                length=-1,
                part_size=MinioClient.part_size
            )
            upload = Upload(
                filename = file.filename,
                minio_object_filename = minio_object_filename,
                uploader = uploader,
                email = email)
            db.add(upload)
            db.commit()
            return "File Uploaded"
        except S3Error as e:
            raise HTTPException(status_code=500, detail=str(e))

    def download(db:Session, bucket_name:str, expire_seconds:int, file_id:int):
        minio_object_filename = db.query(Upload).filter(Upload.id == file_id).first().minio_object_filename
        try:
            url = MinioClient.client.presigned_get_object(bucket_name, minio_object_filename, expires=timedelta(seconds=expire_seconds))
            return url
        except S3Error as e:
            raise HTTPException(status_code=500, detail=str(e))