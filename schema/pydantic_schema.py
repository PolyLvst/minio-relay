from pydantic import BaseModel

class MinIOUploadResponse(BaseModel):
    filename: str | None = None
    url: str | None = None