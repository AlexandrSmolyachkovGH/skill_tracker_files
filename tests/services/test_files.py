from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from file_service.services.files import s3_service
from tests.conftest import (
    MockOutboxRepoMethods,
    MockS3RepoMethods,
)


@pytest.mark.asyncio
async def test_s3service(
    mock_s3_repo_methods: MockS3RepoMethods,
    mock_outbox_repo_methods: MockOutboxRepoMethods,
) -> None:
    _, download_mock = mock_s3_repo_methods
    service = s3_service

    file_name = "test_file"
    attachment_id = uuid4()
    content_type = "application/octet-stream"
    content = file_name.encode()

    key = service.build_key(attachment_id=attachment_id, filename=file_name)
    upload_file_key = await service.upload_file(
        content=content,
        content_type=content_type,
        attachment_id=attachment_id,
        filename=file_name,
    )
    assert upload_file_key == "mocked_file_key"
    service.s3_repo.upload_file.assert_awaited_once()
    service.outbox_repo.add_document.assert_awaited_once()

    content_obj = AsyncMock()
    content_obj.read = AsyncMock(return_value=b"mocked content")

    download_mock.side_effect = [
        (content_obj, "text/plain"),
        None,
        (None, None),
    ]

    data, ctype = await service.download_file(key=key)
    assert data == b"mocked content"
    assert ctype == "text/plain"

    data, ctype = await service.download_file(key=key)
    assert data is None and ctype is None

    data, ctype = await service.download_file(key=key)
    assert data is None and ctype == "application/octet-stream"

    assert download_mock.await_count == 3
