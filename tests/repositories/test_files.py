from unittest.mock import (
    AsyncMock,
)

import pytest


@pytest.mark.asyncio
async def test_upload_file_ok(repo_with_client):
    repo, client, ensure_mock = repo_with_client

    key = await repo.upload_file(
        key="key",
        content_type="text/plain",
        content=b"content",
    )

    assert key == "key"
    ensure_mock.assert_awaited_once_with(client, "test-bucket")
    client.put_object.assert_awaited_once_with(
        Bucket="test-bucket",
        Key="key",
        Body=b"content",
        ContentType="text/plain",
    )


@pytest.mark.asyncio
async def test_download_file_ok(repo_with_client):
    repo, client, _ = repo_with_client
    body = AsyncMock()
    client.get_object.return_value = {
        "Body": body,
        "ContentType": "text/plain",
    }

    content, ctype = await repo.download_file("key")

    assert content is body
    assert ctype == "text/plain"
    client.get_object.assert_awaited_once_with(
        Bucket="test-bucket",
        Key="key",
    )
