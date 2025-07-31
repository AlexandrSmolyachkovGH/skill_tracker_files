import pytest
from pytest_mock import MockerFixture
from unittest.mock import (
    AsyncMock,
    MagicMock,
)

from file_service.config import aws_settings
from file_service.connections.s3_connection import (
    get_s3_client,
    ensure_bucket_exists,
    wait_for_localstack,
)


@pytest.mark.asyncio
async def test_get_s3_client_creates_client(
    session_mock: MagicMock,
    client_mock: AsyncMock,
) -> None:
    session_mock.client.return_value.__aenter__.return_value = client_mock

    async with get_s3_client(session_mock) as client:
        assert client is client_mock
        session_mock.client.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_bucket_exists_already_exists(
    client_mock: AsyncMock,
) -> None:
    client_mock.head_bucket.return_value = None

    await ensure_bucket_exists(client_mock, "test-bucket")
    client_mock.head_bucket.assert_called_once_with(Bucket="test-bucket")
    client_mock.create_bucket.assert_not_called()


@pytest.mark.asyncio
async def test_wait_for_localstack(
    mocker: MockerFixture,
    session_mock: MagicMock,
    mock_response: AsyncMock,
) -> None:
    mock_response.status = 200
    session_mock.get.return_value.__aenter__.return_value = mock_response

    mock_client_session = mocker.patch("aiohttp.ClientSession")
    mock_client_session.return_value.__aenter__.return_value = session_mock

    await wait_for_localstack(aws_settings.S3_ENDPOINT_URL)
