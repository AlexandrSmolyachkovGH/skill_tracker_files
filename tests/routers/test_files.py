from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_upload_file(
    mocker: MockerFixture,
    client: AsyncClient,
) -> None:
    mocker.patch(
        "file_service.services.files.s3_service.upload_file",
        return_value="test_key",
    )
    response = await client.post(
        "/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_download_file_found(
    mocker: MockerFixture,
    client: AsyncClient,
) -> None:
    content = "test bytes".encode("utf-8")
    mocker.patch(
        "file_service.services.files.s3_service.download_file",
        new_callable=AsyncMock,
        return_value=(content, "text/plain"),
    )
    response = await client.post(
        "/download/test_key",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.content == content
    assert response.headers["content-type"].startswith("text/plain")


@pytest.mark.asyncio
async def test_download_file_not_found(
    mocker: MockerFixture,
    client: AsyncClient,
) -> None:
    mocker.patch(
        "file_service.services.files.s3_service.download_file",
        new_callable=AsyncMock,
        return_value=(None, None),
    )
    response = await client.post("/download/missing_key")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.text == '"File not found"'
