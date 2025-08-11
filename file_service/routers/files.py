from io import BytesIO
from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    status,
)
from fastapi.responses import (
    JSONResponse,
    Response,
    StreamingResponse,
)

from file_service.schemes.files import FileUploadResponse
from file_service.services.files import s3_service

router = APIRouter()


@router.post(
    path="/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: Annotated[UploadFile, File(...)],
) -> FileUploadResponse:
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    filename = file.filename or "new_file"

    key = await s3_service.upload_file(
        filename=filename,
        content_type=content_type,
        content=content,
    )

    return FileUploadResponse(key=key)


@router.post(
    path="/download/{key}",
    status_code=status.HTTP_200_OK,
)
async def download_file(
    key: str,
) -> Response:
    content, content_type = await s3_service.download_file(
        key=key,
    )

    if content is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="File not found",
        )

    return StreamingResponse(
        content=BytesIO(content),
        media_type=content_type or "application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={key}",
        },
    )
