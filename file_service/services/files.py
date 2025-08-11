from uuid import uuid4

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
        filename: str,
    ) -> str:
        """
        Create file key for the S3 storage.
        """
        key = f"{uuid4()}_{filename}"
        return key

    async def upload_file(
        self,
        content: bytes,
        content_type: str,
        filename: str,
    ) -> str:
        key = self.build_key(filename=filename)
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
        return file_data


s3_service = S3Service()
