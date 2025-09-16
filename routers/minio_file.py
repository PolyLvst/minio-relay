from fastapi import APIRouter, Form, UploadFile
from config.minio_client import MinioClient
from service.minio_file import MinIOFileService
from schema.pydantic_schema import MinIOUploadResponse

router = APIRouter(prefix="/minio-file")

@router.post("/upload", response_model=MinIOUploadResponse)
def upload_file(file:UploadFile, bucket_name:str = MinioClient.bucket_name):
    return MinIOFileService.upload(bucket_name=bucket_name, file=file)

@router.get("/download/{filename}", response_model=MinIOUploadResponse)
def get_presigned_url(filename: str, bucket_name:str = MinioClient.bucket_name):
    return MinIOFileService.download(bucket_name=bucket_name, filename=filename)