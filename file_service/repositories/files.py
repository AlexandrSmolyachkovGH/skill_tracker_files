from aiobotocore.response import StreamingBody

from file_service.config import aws_settings
from file_service.connections.s3_connection import (
    ensure_bucket_exists,
    get_aws_session,
    get_s3_client,
)


class S3Repository:
    def __init__(self) -> None:
        self.session = get_aws_session()
        self.bucket_name = aws_settings.S3_BUCKET_NAME

    async def upload_file(
        self,
        key: str,
        content_type: str,
        content: bytes,
    ) -> str:
        """
        Upload a file to the S3 bucket.
        """
        async with get_s3_client(self.session) as client:
            await ensure_bucket_exists(client, self.bucket_name)
            await client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
            )
        return key

    async def download_file(
        self, key: str
    ) -> tuple[StreamingBody | None, str | None]:
        """
        Get a file from the S3 bucket.
        """
        async with get_s3_client(self.session) as client:
            try:
                response = await client.get_object(
                    Bucket=self.bucket_name,
                    Key=key,
                )
                return response["Body"], response["ContentType"]
            except client.exceptions.NoSuchKey:
                return None, None


s3_repo = S3Repository()
