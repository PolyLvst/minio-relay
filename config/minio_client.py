from minio import Minio
import os

class MinioClient:
    client = Minio(
        os.getenv("MINIO_ENDPOINT", "minio:9000"),
        access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
        secure=False,
    )
    # controls chunk size for multipart uploads.
    part_size = 10*1024*1024
    bucket_name = os.getenv("MINIO_RELAY_BUCKET_NAME", "miniorelay")
