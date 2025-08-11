import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiohttp
from aioboto3 import Session
from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError

from file_service.config import aws_settings


def get_aws_session() -> Session:
    return Session()


@asynccontextmanager
async def get_s3_client(
    session: Session,
) -> AsyncGenerator[AioBaseClient, None]:
    async with session.client(
        "s3",
        endpoint_url=aws_settings.S3_ENDPOINT_URL,
        aws_access_key_id=aws_settings.AWS_ACCESS_KEY_ID.get_secret_value(),
        aws_secret_access_key=aws_settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
        region_name=aws_settings.AWS_DEFAULT_REGION,
    ) as client:
        yield client


async def ensure_bucket_exists(
    client: AioBaseClient,
    bucket_name: str,
) -> None:
    try:
        await client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("404", "NoSuchBucket"):
            await client.create_bucket(Bucket=bucket_name)
        elif error_code == "403":
            raise RuntimeError(f"Access denied to bucket {bucket_name}")
        else:
            raise


async def wait_for_localstack(
    url: str,
    retries: int = 10,
    delay: float = 1.0,
) -> None:
    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return
        except Exception as e:
            print(f"Wait for localstack(attempt {attempt}) — {e}")
        await asyncio.sleep(delay)
    raise RuntimeError(f"LocalStack")
