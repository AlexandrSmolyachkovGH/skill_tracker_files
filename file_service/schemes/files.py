from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    key: str
