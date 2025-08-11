import inspect
import re
from uuid import UUID

from file_service.repositories.files import (
    S3Repository,
    s3_repo,
)
from file_service.repositories.outbox import (
    OutboxMongoRepository,
    outbox_repository,
)


class S3Service:
    def __init__(
        self,
        s3repo: S3Repository = s3_repo,
        outbox_repo: OutboxMongoRepository = outbox_repository,
    ) -> None:
        self.s3_repo = s3repo
        self.outbox_repo = outbox_repo

    def build_key(
        self,
        attachment_id: UUID,
        filename: str,
    ) -> str:
        """
        Generate a unique file key for S3 storage
        """
        filename = re.sub(r"\s", "_", filename)
        key = f"{attachment_id}_{filename}"
        return key

    async def upload_file(
        self,
        attachment_id: UUID,
        content: bytes,
        content_type: str,
        filename: str,
    ) -> str:
        key = self.build_key(
            attachment_id=attachment_id,
            filename=filename,
        )
        key = await s3_repo.upload_file(
            key=key,
            content_type=content_type,
            content=content,
        )
        document = {"key": key}
        await self.outbox_repo.add_document(document)
        return key

    async def download_file(
        self,
        key: str,
    ) -> tuple:
        file_data = await s3_repo.download_file(
            key=key,
        )
        if file_data is None:
            return None, None

        content, content_type = file_data

        if content is None:
            return None, (content_type or "application/octet-stream")

        if hasattr(content, "read"):
            result = content.read()
            content = await result if inspect.isawaitable(result) else result

        return content, content_type or "application/octet-stream"


s3_service = S3Service()
